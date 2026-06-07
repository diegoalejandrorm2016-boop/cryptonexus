# TODO - Perfil de usuario + notificación por correo

- [x] 1) Agregar campos al modelo User: `age` (IntegerField) y `profile_photo` (ImageField).
- [x] 2) Crear formulario `ProfileForm` para editar nombre/edad y foto.
- [x] 3) Crear vista protegida `profile_view` y template `templates/dashboard/profile.html`.
- [x] 4) Agregar ruta en `trading/urls.py` y enlace en `base.html`.
- [x] 5) Crear función de email para notificar el registro (`send_welcome_email`) usando Gmail via settings existentes.
- [x] 6) Llamar a esa función desde `register_view` después de crear el usuario.
- [x] 7) Configurar `MEDIA_URL` y `MEDIA_ROOT` en `cryptonexus/settings.py` (y servir media en urls si aplica).
- [ ] 8) Crear migración y aplicar (`python manage.py makemigrations` y `migrate`).
- [ ] 9) Probar: registrar usuario → validar que llegue el correo; editar perfil → validar que persistan cambios y se muestre foto.


