from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import UserLead
from .email_utils import send_email

@receiver(post_save, sender=UserLead)
def hangout_created(sender, instance, created, **kwargs):
    if created:
        title = "New Lead"
        msg = f"you have a new lead with the following info \n" \
              f"email: {instance.email}\n"\
              f"name: {instance.name}\n"\
              f"phone: {instance.phone}\n"\
              f"website: {instance.website}\n"
        send_email("hise1010@gmail.com", title, msg)
        # send_email("aaronorosen2@gmail.com", "New Lead")