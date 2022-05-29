from django.conf import settings
from django.db import models

# Create your models here.
class Recipe(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(max_length=255)
    text = models.TextField()
    ingredients = models.ManyToManyField('Ingredient', related_name='recipes')
    ratings = models.ManyToManyField(settings.AUTH_USER_MODEL, through='RecipeRating')

    @property
    def _avg_rating(self):
        return self.recipe_ratings.aggregate(models.Avg('rate'))['rate__avg']

    def update_rating(self, user: settings.AUTH_USER_MODEL, rate: int):
        if user in self.ratings.all():
            rating = self.recipe_ratings.get(user=user)
            rating.rate = rate
            rating.save(update_fields=['rate'])
        else:
            rating = RecipeRating(rate=rate, user=user, recipe=self)
            rating.save()


class Ingredient(models.Model):
    name = models.CharField(max_length=255)


class RecipeRating(models.Model):
    rate = models.IntegerField(default=1)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, related_name='recipe_ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipe_ratings')

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(rate__gte=1, rate__lte=5), name='rate_validation'),
            models.UniqueConstraint(fields=['recipe', 'user'], name='unique_user_per_recipe')
        ]