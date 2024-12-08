from django.db import migrations, models
import django.db.models.deletion

def create_categories(apps, schema_editor):
    MenuItem = apps.get_model('restaurant_app', 'MenuItem')
    MenuCategory = apps.get_model('restaurant_app', 'MenuCategory')
    Restaurant = apps.get_model('restaurant_app', 'Restaurant')
    
    # Get all unique category names and restaurants
    for item in MenuItem.objects.all():
        category_name = item.category
        restaurant = item.restaurant
        MenuCategory.objects.get_or_create(
            name=category_name,
            restaurant=restaurant,
            defaults={'description': f'Category for {category_name}'}
        )

def link_categories(apps, schema_editor):
    MenuItem = apps.get_model('restaurant_app', 'MenuItem')
    MenuCategory = apps.get_model('restaurant_app', 'MenuCategory')
    
    for item in MenuItem.objects.all():
        category = MenuCategory.objects.get(
            name=item.category,
            restaurant=item.restaurant
        )
        item.new_category = category
        item.save()

class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0005_restaurantcategory_restaurant_is_verified_and_more'),
    ]

    operations = [
        # Add temporary category field
        migrations.AddField(
            model_name='menuitem',
            name='new_category',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='new_items',
                to='restaurant_app.menucategory'
            ),
        ),
        
        # Create categories
        migrations.RunPython(create_categories),
        
        # Link items to categories
        migrations.RunPython(link_categories),
        
        # Remove old category field
        migrations.RemoveField(
            model_name='menuitem',
            name='category',
        ),
        
        # Rename new_category to category
        migrations.RenameField(
            model_name='menuitem',
            old_name='new_category',
            new_name='category',
        ),
        
        # Make category required
        migrations.AlterField(
            model_name='menuitem',
            name='category',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='menu_items',
                to='restaurant_app.menucategory'
            ),
        ),
    ] 