from rest_framework import serializers
from .models import ShopUser, Address

class RegisterSerializer(serializers.ModelSerializer):
    province = serializers.CharField(write_only=True)
    city = serializers.CharField(write_only=True)
    detail_address = serializers.CharField(write_only=True)

    class Meta:
        model = ShopUser
        fields = ['username', 'email', 'password', 'province', 'city', 'detail_address']
        extra_kwargs = {
            'password': {'write_only': True}, 
        }

    def create(self, validated_data):
        province = validated_data.pop('province')
        city = validated_data.pop('city')
        detail_address = validated_data.pop('detail_address')

        user = ShopUser.objects.create_user(**validated_data)

        Address.objects.create(
            user=user, 
            province=province, 
            city=city, 
            detail_address=detail_address
        )
        return user