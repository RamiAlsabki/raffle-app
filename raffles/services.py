import random
from .models import Ticket

def draw_winners(raffle):
    ticket_numbers = list(raffle.tickets.values_list('ticket_number', flat=True))
    
    for prize in raffle.prizes.all():

        for _ in range(prize.amount):
            random.shuffle(ticket_numbers)
            if ticket_numbers:
                winning_ticket = ticket_numbers.pop()
                Ticket.objects.filter(ticket_number=winning_ticket).update(
                    has_won=True,
                    prize=prize.name
                )
    
    raffle.winners_drawn = True
    raffle.save()
    return Ticket.objects.filter(has_won=True)



def issue_ticket_number(raffle):
    existing_ticket_numbers = list(raffle.tickets.values_list('ticket_number', flat=True))
    next_ticket = random.choice([i for i in range(1, raffle.total_tickets+1) 
                                 if i not in existing_ticket_numbers])
    return next_ticket