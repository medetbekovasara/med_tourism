# MedTour - Medical Tourism Platform

MedTour is a Django-based web platform developed for facilitating medical tourism in Kyrgyzstan. It allows users to browse clinics, doctors, and hotels, book medical consultations, hotel stays, and clinic treatments, and manage their bookings in one unified platform. The project was created as a final thesis project by Sara Medetbekova.

## Features

* User registration, login, and profile management
* Booking system for:

  * Medical consultations with doctors
  * Stays in partner hotels
  * Treatments in medical clinics
* User dashboard with upcoming bookings and cancel options
* Multilingual support (English and Russian)
* Responsive front-end with Bootstrap 5
* Admin panel for managing content (clinics, doctors, hotels, bookings)

## Technologies Used

* Python 3.9
* Django 4.2
* PostgreSQL
* HTML, CSS (Bootstrap 5)
* JavaScript (for dynamic forms and dropdowns)

## Project Structure

```
med_tourism/
├── account/             # Handles user profiles and authentication
├── tourism/             # Core app for clinics, hotels, and bookings
├── templates/           # Shared templates
├── static/              # CSS, JS, images
├── media/               # Uploaded media files
├── manage.py            # Django management script
```

## How to Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/medtour.git
   cd medtour
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:

   ```bash
   python manage.py migrate
   ```

5. Create a superuser:

   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:

   ```bash
   python manage.py runserver
   ```

7. Access the site at:

   * `http://127.0.0.1:8000/` – main website
   * `http://127.0.0.1:8000/admin/` – admin panel

## Customizations & Highlights

* Consultation cancellations are only possible 5 hours before the appointment.
* Hotel and clinic bookings can be canceled up to 5 days before check-in.
* Bookings are visually categorized by status: confirmed, pending, or canceled.
* User-friendly dashboard with appointment and booking history.

## Deployment Notes

For deployment, the platform supports PostgreSQL, and can be hosted on services such as Heroku, DigitalOcean, or Render. For production, be sure to:

* Set `DEBUG = False`
* Configure static and media file hosting
* Use environment variables for sensitive data

## License

This project is for academic use and demonstration. Please contact the author for commercial or collaboration inquiries.

## Author

Sara Medetbekova – Applied Mathematics and Informatics Faculty

Email: [medetbekovasara1@gmail.com](mailto:medetbekovasara1@gmail.com)
Location: Bishkek, Kyrgyzstan
