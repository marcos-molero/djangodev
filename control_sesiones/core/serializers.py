from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class AccessTokenOnlySerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        return {
            'access': data['access'],
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
            }
        }
