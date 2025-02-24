# print("DEBUG: Starting to load views for organizations app...")

# from django.shortcuts import render, get_object_or_404, redirect
# from django.http import JsonResponse
# from django.http import HttpResponseRedirect
# from django.core.paginator import Paginator
# from .models import OrganizationType
# from .forms import OrganizationTypeForm

# def organization_type_manage(request):
#     # Fetch and paginate organization types (10 per page)
#     paginator = Paginator(OrganizationType.objects.all(), 10)
#     page_number = request.GET.get('page')
#     types = paginator.get_page(page_number)

#     # Handle the form for adding a new organization type
#     if request.method == 'POST' and request.POST.get('form_name') == 'add_type_form':
#         add_form = OrganizationTypeForm(request.POST)
#         if add_form.is_valid():
#             add_form.save()
#             return redirect('organizations:organization_type_manage')
        
#         else:
#             messages.error(request, 
#                 _('Failed to add organization type. Please fix the errors below.'))
#     else:
#         add_form = OrganizationTypeForm()

#     # Render the page
#     return render(request, 'organizations/organization_types.html', {
#         'types': types,
#         'add_form': add_form,
#     })

# def get_organization_type_details(request, pk):
#     """API endpoint to fetch organization type details."""
#     try:
#         org_type = get_object_or_404(OrganizationType, pk=pk)
#         data = {
#             'name': org_type.name,
#             'description': org_type.description,
#         }
#         return JsonResponse(data, status=200)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=400)

# def get_organization_type_description(request):
    
#     # API endpoint to fetch the description of organization type based on name.

#     if request.method == 'GET' and 'name' in request.GET:
#         # Extract the 'name' parameter from the request
#         name = request.GET['name']
        
#         # Look up the organization type by name
#         org_type = OrganizationType.objects.filter(name=name).first()
        
#         if org_type:
#             # Return the description if the organization type exists
#             return JsonResponse({'description': org_type.description})
        
#         # If no organization type is found, return an empty description
#         return JsonResponse({'description': ''})
    
#     # If the request is invalid, return an error response
#     return JsonResponse({'error': 'Invalid request'}, status=400)

# def edit_organization_type(request, pk):
#     organization_type = get_object_or_404(OrganizationType, pk=pk)

#     if request.method == 'GET':
#         # Return the organization type data as JSON
#         return JsonResponse({
#             'name': organization_type.name,
#             'description': organization_type.description,
#         })

#     elif request.method == 'POST':
#         # Update the organization type
#         form = OrganizationTypeForm(request.POST, instance=organization_type)
#         if form.is_valid():
#             form.save()
#             return redirect('organizations:organization_type_manage')
        
#         else:
#             messages.error(
#                 request, _('Failed to edit organization type. Please fix the errors below.'))

#     # Render the edit form with errors (if any)
#     return render(request, 'organizations/organization_types.html', {
#         'edit_form': form,
#     })
    
# def delete_organization_type(request, pk):
#     # Fetch the organization type or return a 404 if not found
#     organization_type = get_object_or_404(OrganizationType, pk=pk)

#     if request.method == 'POST':
#         # Delete the organization type
#         organization_type.delete()
#         return redirect('organizations:organization_type_manage')

#     # Redirect or return an error if the request method is not POST
#     return HttpResponseRedirect('organizations:organization_type_manage')

# def organization_list(request):
#     # Fetch all organizations
#     organizations = Organization.objects.all()

#     # Render the organization list template
#     return render(request, 'organizations/organization_list.html', {
#         'organizations': organizations,
#     })

# def organization_detail(request, pk):
#     # Fetch the organization by primary key or return 404 if not found
#     organization = get_object_or_404(Organization, pk=pk)

#     # Fetch related contacts using the updated related_name
#     contacts = organization.organization_contacts.all()

#     # Render the organization detail template
#     return render(request, 'organizations/organization_detail.html', {
#         'organization': organization,
#         'contacts': contacts,
#     })

# print("DEBUG: Finished loading views for organizations app.")