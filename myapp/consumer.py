# consumer.py
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from myapp.models import Contact, UserStatus

class ContactConsumer(WebsocketConsumer):

    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)("contacts", self.channel_name)
        user = self.scope["user"]
        if user.is_authenticated:
            UserStatus.objects.update_or_create(user=user, defaults={"is_online": True})

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("contacts", self.channel_name)
        user = self.scope["user"]
        if user.is_authenticated:
            UserStatus.objects.filter(user=user).update(is_online=False)

    def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'load_contacts':
            self.load_contacts()
        elif action == 'add_contact':
            self.add_contact(data)
        elif action == 'edit_contact':
            self.edit_contact(data)
        elif action == 'delete_contact':
            self.delete_contact(data)

    def load_contacts(self):
        contacts = Contact.objects.all().values('id', 'name', 'email', 'phone_number', 'address')
        self.send(text_data=json.dumps({'action': 'load_contacts', 'contacts': list(contacts)}))

    def add_contact(self, data):
        contact = Contact.objects.create(
            name=data['name'],
            email=data['email'],
            phone_number=data['phone_number'],
            address=data['address']
        )
        self.broadcast_changes('add_contact', contact)

    def edit_contact(self, data):
        contact = Contact.objects.get(id=data['id'])
        contact.name = data['name']
        contact.email = data['email']
        contact.phone_number = data['phone_number']
        contact.address = data['address']
        contact.save()
        self.broadcast_changes('edit_contact', contact)

    def delete_contact(self, data):
        contact = Contact.objects.get(id=data['id'])
        contact.delete()
        async_to_sync(self.channel_layer.group_send)(
            "contacts",
            {
                "type": "contact_message",
                "action": "delete_contact",
                "id": data['id']
            }
        )

    def broadcast_changes(self, action, contact):
        async_to_sync(self.channel_layer.group_send)(
            "contacts",
            {
                "type": "contact_message",
                "action": action,
                "contact": {
                    'id': contact.id,
                    'name': contact.name,
                    'email': contact.email,
                    'phone_number': contact.phone_number,
                    'address': contact.address
                }
            }
        )

    def contact_message(self, event):
        self.send(text_data=json.dumps(event))
