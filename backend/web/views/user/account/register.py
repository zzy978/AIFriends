from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from web.models.user import UserProfile
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            username = request.data['username'].strip()
            password = request.data['password'].strip()
            if not username or not password:
                return Response({
                    'result': '用户名和密码不能为空'
                })
            if User.objects.filter(username=username).exists():
                return Response({
                    'result': '用户名已存在'
                })
            user = User.objects.create_user(username=username, password=password)
            user_profile = UserProfile.objects.create(user=user)
            refresh = RefreshToken.for_user(user) # 生成JWT token
            response = Response({
                'result': 'success',
                'access': str(refresh.access_token),
                'user_id': user.id,
                'username': user.username,
                'photo': user_profile.photo.url,
                'profile': user_profile.profile 
            })
            response.set_cookie(
                key = 'refresh_token',
                value = str(refresh),
                httponly = True,
                samesite = 'Lax',
                secure = True,
                max_age = 7 * 24 * 60 * 60
            )
            return response

        except:
            return Response({
                'result': '系统异常，请稍后再试'
            })