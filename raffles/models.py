import uuid
import random
from django.db import models
from django.core.validators import MinValueValidator, validate_ipv46_address

class Raffle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    total_tickets = models.IntegerField(null=False)
    available_tickets = models.IntegerField()
    winners_drawn = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.name
    
        """ returns a raffle ticket in a non-sequential order"""
    def get_ticket_number(self):
        # get all existing ticket numbers in a list
        existing_ticket_numbers = list(
            self.tickets.values_list('ticket_number', flat=True))
        # get a random ticket from 0....total_tickets excluding the ones already issues
        next_ticket = random.choice([i for i in range(1, self.total_tickets+1)
                                     if i not in existing_ticket_numbers])
        return next_ticket
    
    def draw_winners(self):
        ticket_numbers = list(self.tickets.values_list('ticket_number', flat=True))
        for prize in self.prizes.all():
            for i in range(0, prize.amount):
                random.shuffle(ticket_numbers)
                winning_ticket = ticket_numbers.pop()
                Ticket.objects.filter(id=winning_ticket).update(
                    has_won=True,
                    prize=prize.name
                )
        self.winners_drawn = True
        self.save()
        return Ticket.objects.filter(has_won=True)
    

class Ticket(models.Model):
    raffle = models.ForeignKey(Raffle, related_name='tickets', on_delete=models.CASCADE)
    ticket_number = models.IntegerField()
    verification_code = models.UUIDField(editable=False, default=uuid.uuid4)
    has_won = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(validators=[validate_ipv46_address])
    prize = models.CharField(default=None, max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ('-created_at'),
        unique_together = (('raffle', 'ticket_number'), ('raffle', 'ip_address'))


class Prize(models.Model):
    name = models.TextField()
    amount = models.IntegerField()
    raffle = models.ForeignKey(Raffle, related_name='prizes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    
