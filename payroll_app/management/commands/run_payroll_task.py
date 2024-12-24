import calendar
import pprint
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.core.mail import send_mail
from django.conf import settings
from django.core.management.base import BaseCommand
from ...models import User, PayrollManagement

def calculate_payroll_for_users():
    pp = pprint.PrettyPrinter(indent=4)  
    # Get the current date and determine the previous month
    current_date = timezone.now()
    current_month = current_date.month
    current_year = current_date.year
    # Calculate the previous month and year
    previous_month = current_month - 1 if current_month > 1 else 12
    previous_year = current_year if current_month > 1 else current_year - 1
    # Get all users
    users = User.objects.all()
    for user in users:
        # Check if the user is verified
        if not user.verified:
            pp.pprint(f"User {user.first_name} is not verified.")
            continue
        # Check if payroll for this month and year already exists
        if PayrollManagement.objects.filter(user=user, month=previous_month, year=previous_year).exists():
            pp.pprint(f"Payroll for user {user.first_name} for {previous_month}/{previous_year} already exists.")
            continue
        # Calculate payroll values for each user
        annual_salary = user.annual_salary  # Assuming user has an 'annual_salary' field
        gross_salary = round(annual_salary / 12, 2)  # Monthly gross salary
        provident_fund = round(gross_salary * 0.04, 2)  # 4% of gross salary
        if gross_salary <= 7500:
            professional_tax = 0
        elif 7501 <= gross_salary <= 10000:
            professional_tax = 175
        else:
            professional_tax = 200
        num_days_in_month = calendar.monthrange(previous_year, previous_month)[1]
        loss_of_pay = round(((gross_salary - provident_fund - professional_tax) / num_days_in_month) * user.leaves, 2)
        net_salary = round(gross_salary - provident_fund - professional_tax - loss_of_pay, 2)
        # Create or update PayrollManagement instance for the previous month
        PayrollManagement.objects.update_or_create(
            user=user,
            month=previous_month,
            year=previous_year,
            defaults={
                'gross_salary': gross_salary,
                'provident_fund': provident_fund,
                'professional_tax': professional_tax,
                'loss_of_pay': loss_of_pay,
                'net_salary': net_salary
            }
        )
        # Send email to the user
        subject = 'Payroll Calculated for {}/{}'.format(previous_month, previous_year)
        html_message = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payroll Details</title>
        </head>
        <body>
            <p>Dear {},</p>
            <p>Your payroll for {}/{} has been calculated. Below are the details:</p>
            <ul>
                <li>Monthly Salary: {}</li>
                <li>Provident Fund: {}</li>
                <li>Professional Tax: {}</li>
                <li>Loss of Pay: {}</li>
                <li>Net Salary: {}</li>
            </ul>
            <p>Thank you.</p>
        </body>
        </html>
        """.format(
            user.first_name,
            previous_month,
            previous_year,
            gross_salary,
            provident_fund,
            professional_tax,
            loss_of_pay,
            net_salary
        )
        send_mail(subject, '', settings.EMAIL_HOST_USER, [user.email], html_message=html_message)
        # Print payroll calculation details
        pp.pprint({
            'User': user.first_name,
            'Month': previous_month,
            'Year': previous_year,
            'Gross Salary': gross_salary,
            'Provident Fund': provident_fund,
            'Professional Tax': professional_tax,
            'Loss of Pay': loss_of_pay,
            'Net Salary': net_salary
        })

class Command(BaseCommand):
    help = 'Runs the payroll task using APScheduler'

    def handle(self, *args, **kwargs):
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")
        # Schedule the task to run every 10 seconds for testing purposes
        scheduler.add_job('payroll_app.management.commands.run_payroll_task:calculate_payroll_for_users',  trigger='cron',  day=1,  hour=0,  minute=0)
        scheduler.start()
        self.stdout.write(self.style.SUCCESS('Scheduler started. Press Ctrl+C to exit.'))
        try:
            # Keep the process alive
            while True:
                pass
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            self.stdout.write(self.style.SUCCESS('Scheduler stopped.'))
            print("Scheduler is down.")
