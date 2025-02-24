# from django.db.models.signals import post_save, post_migrate
# from django.dispatch import receiver
# from django.core.mail import send_mail
# from django.contrib.auth.hashers import make_password
# from .models import User
# # Use our custom models
# # from authorization.models import Role, UserRole, RolePermission


# # Hashes plaintext passwords from fixture after migrations.
# @receiver(post_migrate)
# def hash_fixture_passwords(sender, **kwargs):
#     if sender.name == "users":
#         for user in User.objects.all():
#             if not user.password.startswith("pbkdf2_sha256$"):
#                 user.password = make_password(user.password)
#                 user.save()

# # Decorator listens for the post_save signal on the User model
# # @receiver(post_save, sender=User)
# # def send_welcome_email(sender, instance, created, **kwargs):
# #     if created:
# #         # Check if the user has a specific role (e.g., "Manager")
# #         manager_role = Role.objects.filter(name="Manager").first()
# #         if manager_role and UserRole.objects.filter(user=instance, role=manager_role).exists():
# #             # Send email if the user has the "Manager" role
# #             send_mail(
# #                 'Welcome to QWIIT',
# #                 'Hello, welcome to our QWIIT! Your account has been created successfully.',
# #                 'from@example.com',
# #                 [instance.email],
# #                 fail_silently=False,
# #             )
# #             instance.welcome_email_sent = True
# #             instance.save()
# #             print(f"Welcome email sent to {instance.email}")

# #         # Check if the user has a specific custom permission
# #         permission = RolePermission.objects.filter(permission__codename="can_receive_welcome_email").first()
# #         if permission and UserRole.objects.filter(user=instance, role=permission.role).exists():
# #             # Send email if the permission is assigned via a role
# #             send_mail(
# #                 'Welcome to QWIIT',
# #                 'Hello, welcome to our QWIIT! Your account has been created successfully.',
# #                 'from@example.com',
# #                 [instance.email],
# #                 fail_silently=False,
# #             )
# #             instance.welcome_email_sent = True
# #             instance.save()
# #             print(f"Welcome email sent to {instance.email}")
