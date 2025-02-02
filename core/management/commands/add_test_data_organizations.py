from django.core.management.base import BaseCommand
from organizations.models import Organization, OrganizationType, OrganizationContact
from django.utils.timezone import now
import json

class Command(BaseCommand):
    help = "Add test data for organizations"

    def handle(self, *args, **kwargs):
        self.stdout.write("\nAdding test data for organizations...\n")

        # Create Organizations with Description
        OrganizationType = [
            {"name": "Healthcare", "description": "Medical institutions and health services"},
            {"name": "Tech", "description": "Technology and software companies"},
            {"name": "Education", "description": "Schools, universities, and educational services"},
        ]

        organization_type_objects = []
        for data in OrganizationType:
            obj, created = OrganizationType.objects.get_or_create(
                name=data["name"],
                defaults={"description": data["description"]}
            )
            organization_type_objects.append(obj)

        # Create Organizations
        Organization = [
            {
                "name": "City Hospital",
                "type": organization_type_objects[0],  # Healthcare
                "active": True,
                "login_options": json.dumps({"allow_email_login": True, 
                                             "allow_username_login": True,
                                             "allow_badge_barcode_login": False,
                                             "allow_badge_rfid": False,
                                             }),
                "mfa_required": True,
                "date_created": now(),
                "created_by": "test_admin",
                "last_modified": now(),
                "modified_by": "test_admin",
            },
            {
                "name": "Acme Tech",
                "type": organization_type_objects[1],  # Tech
                "active": True,
                "login_options": json.dumps({"allow_email_login": True, 
                                             "allow_username_login": False,
                                             "allow_badge_barcode_login": False,
                                             "allow_badge_rfid": False,
                                             }),
                "mfa_required": False,
                "date_created": now(),
                "created_by": "test_admin",
                "last_modified": now(),
                "modified_by": "test_admin",
            },
            {
                "name": "Springfield University",
                "type": organization_type_objects[2],  # Education
                "active": True,
                "login_options": json.dumps({"allow_email_login": False, 
                                             "allow_username_login": True,
                                             "allow_badge_barcode_login": False,
                                             "allow_badge_rfid": False,
                                             }),
                "mfa_required": True,
                "date_created": now(),
                "created_by": "test_admin",
                "last_modified": now(),
                "modified_by": "test_admin",
            },
        ]   
        
        Organization_objects = []
        for Organization_data in Organization:
            obj, created = Organization.objects.get_or_create(
                name=Organization_data["name"],
                defaults={
                    "type": Organization_data["type"],
                    "active": Organization_data["active"],
                    "login_options": Organization_data["login_options"],
                    "mfa_required": Organization_data["mfa_required"],
                    "date_created": Organization_data["date_created"],
                    "created_by": Organization_data["created_by"],  # Just a string, no user checks
                    "last_modified": Organization_data["last_modified"],
                    "modified_by": Organization_data["modified_by"],  # Just a string, no user checks
                }
            )
            Organization_objects.append(obj)

        # Create Contacts
        OrganizationContact = [
            {
                "first_name": "Alice",
                "last_name": "Johnson",
                "organization": Organization_objects[0],  # City Hospital
                "email": "alice@cityhospital.com",
                "phone_number": "555-1234",
                "address": "123 Medical St, Cityville",
                "role": "Chief Medical Officer",
                "date_created": now(),
                "created_by": "test_admin",
                "last_modified": now(),
                "modified_by": "test_admin",
            },
            {
                "first_name": "Bob",
                "last_name": "Smith",
                "organization": Organization_objects[1],  # Acme Tech
                "email": "bob@acmetech.com",
                "phone_number": "555-5678",
                "address": "456 Innovation Dr, TechTown",
                "role": "CTO",
                "date_created": now(),
                "created_by": "test_admin",
                "last_modified": now(),
                "modified_by": "test_admin",
            },
            {
                "first_name": "Charlie",
                "last_name": "Davis",
                "organization": Organization_objects[2],  # Springfield University
                "email": "charlie@springedu.com",
                "phone_number": "555-9876",
                "address": "789 College Ave, Springfield",
                "role": "Dean of Admissions",
                "date_created": now(),
                "created_by": "test_admin",
                "last_modified": now(),
                "modified_by": "test_admin",
            },
        ]    
        
        for OrganizationContact in OrganizationContact:
            OrganizationContact.objects.get_or_create(
                first_name=OrganizationContact["first_name"],
                last_name=OrganizationContact["last_name"],
                organization=OrganizationContact["organization"],
                defaults={
                    "email": OrganizationContact["email"],
                    "phone_number": OrganizationContact["phone_number"],
                    "address": OrganizationContact["address"],
                    "role": OrganizationContact["role"],
                    "date_created": OrganizationContact["date_created"],
                    "created_by": OrganizationContact["created_by"],  # Just a string, no user checks
                    "last_modified": OrganizationContact["last_modified"],
                    "modified_by": OrganizationContact["modified_by"],  # Just a string, no user checks
                }
            )

        self.stdout.write("\n Test data for organizations added successfully.\n")