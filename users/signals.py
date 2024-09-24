from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import User
from django.contrib.auth.models import Group, Permission

# Decorator listens for the post_save signal on the User model
@receiver(post_save, sender=User)
# Function is the handler for the signal
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        # Check if the user is in a specific group (e.g., "Manager")
        group = Group.objects.filter(name="Manager").first()
        if group and group in instance.groups.all():
            # Send email if part of the group
            send_mail(
                'Welcome to QWIIT',
                'Hello, welcome to our QWIIT! Your account has been created successfully.',
                # Sender email
                'from@example.com',
                # Recipient email (newly created user)
                [instance.email],
                fail_silently=False,
            )
            # Update the field
            instance.welcome_email_sent = True
            # Save the change to the database
            instance.save()
            # Print statement only for development and testing, comment out in production           
            print(f"Welcome email sent to {instance.email}")

        # Check if the user has a specific permission (e.g., "can_receive_welcome_email")
        permission = Permission.objects.filter(codename="can_receive_welcome_email").first()
        if permission and permission in instance.user_permissions.all():
            # Send email if the permission is assigned
            send_mail(
                'Welcome to QWIIT',
                'Hello, welcome to our QWIIT! Your account has been created successfully.',
                # Sender email                
                'from@example.com',
                # Recipient email (newly created user)
                [instance.email],
                fail_silently=False,
            )
            
            # Update the field
            instance.welcome_email_sent = True
            # Save the change to the database
            instance.save()
            # Print statement only for development and testing, comment out in production           
            print(f"Welcome email sent to {instance.email}")