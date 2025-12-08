# QR Café — Django Example (v2)
Now includes:
- Browser geolocation ("Use my location") → stored in session
- Admin-editable default lat/lon (Core → Site Settings)
- Weather-based menu using session → site default → project default fallback
- QR payments flow, inventory auto-deduct, email bill, analytics

## Quickstart
```
python -m venv venv && source venv/bin/activate  # on Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
- Go to **/admin**, open **Site Settings** to set default coordinates.
- Visit **/menu/today/** and click **Use my location** to personalize the menu.
