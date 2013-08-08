from __future__ import absolute_import

from django.core.management.base import BaseCommand

from zerver.lib.actions import do_update_message_flags
from zerver.models import UserProfile, Message, get_user_profile_by_email

class Command(BaseCommand):
    help = """Bankrupt one or many users.

Usage: python manage.py bankrupt_users <list of email addresses>"""

    def handle(self, *args, **options):
        if len(args) < 1:
            print "Please provide at least one e-mail address."
            exit(1)

        for email in args:
            try:
                user_profile = get_user_profile_by_email(email)
            except UserProfile.DoesNotExist:
                print "e-mail %s doesn't exist in the system, skipping" % (email,)
                continue

            do_update_message_flags(user_profile, "add", "read", None, True)

            messages = Message.objects.filter(
                usermessage__user_profile=user_profile).order_by('-id')[:1]
            if messages:
                old_pointer = user_profile.pointer
                new_pointer = messages[0].id
                user_profile.pointer = new_pointer
                user_profile.save(update_fields=["pointer"])
                print "%s: %d => %d" % (email, old_pointer, new_pointer)
            else:
                print "%s has no messages, can't bankrupt!" % (email,)
