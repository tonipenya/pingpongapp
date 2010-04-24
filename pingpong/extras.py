
# Extra url for creating an admin user for local development - this goes in urls.py
(r'^create_admin_user$', 'create_admin_user'),

# Extra view for creating admin user for local development - this goes in views.py
def create_admin_user(request):
    user = User.get_by_key_name('admin')
    if not user or user.username != 'admin' or not (user.is_active and
            user.is_staff and user.is_superuser and
            user.check_password('admin')):
        user = User(key_name='admin', username='admin',
            email='admin@localhost', first_name='Boss', last_name='Admin',
            is_active=True, is_staff=True, is_superuser=True)
        user.set_password('admin')
        user.put()
    return render_to_response(request, 'pingpong/index.html')
