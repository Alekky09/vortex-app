from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

from recipes.models import Recipe, Ingredient
from recipes.services.hunter import HunterClient


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': "Password fields didn't match."})
        hunter_client = HunterClient()
        if not hunter_client.is_email_valid(attrs['email']):
            raise serializers.ValidationError({'email': 'Email is not valid.'})
        return attrs

    def create(self, validated_data):
        user = get_user_model().objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class RecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    text = serializers.CharField()
    ingredients = serializers.ListField(write_only=True, child=serializers.CharField())
    ingredients_list = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('name', 'text', 'ingredients', 'avg_rating', 'ingredients_list')
        read_only_fields = ('avg_rating', 'ingredients_list')

    def get_avg_rating(self, obj):
        return obj.avg_rating if hasattr(obj, 'avg_rating') else obj._avg_rating

    def get_ingredients_list(self, obj):
        return obj.ingredients.values_list('name', flat=True)

    def create(self, validated_data):
        recipe = Recipe(
            user=self.context['user'],
            name=validated_data['name'],
            text=validated_data['text']
        )
        recipe.save()
        existing_ingredients = Ingredient.objects.filter(name__in=validated_data['ingredients'])
        if existing_ingredients.exists():
            ingredients_names = set(existing_ingredients.values_list('name', flat=True))
            new_names = set(validated_data['ingredients']).difference(ingredients_names)
        else:
            new_names = validated_data['ingredients']
        new_ingredients = [Ingredient(name=name) for name in new_names]
        Ingredient.objects.bulk_create(new_ingredients, ignore_conflicts=True)
        all_ingredients = Ingredient.objects.filter(name__in=validated_data['ingredients'])
        recipe.ingredients.add(*all_ingredients)
        return recipe


class RateSerializer(serializers.Serializer):
    rate = serializers.IntegerField()

    def validate_rate(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError({"rate": "Rate should be and integer between 1 and 5."})
        return value

    def validate(self, attrs):
        if self.context['recipe'].user == self.context['user']:
            raise serializers.ValidationError('You cannot rate your own recipe!')
        return attrs


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name')
