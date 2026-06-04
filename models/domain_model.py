"""
B-UML structural model for the theatre reservation domain (Lab 1 / Full Web App generation).
"""
from besser.BUML.metamodel.structural import (
    BinaryAssociation,
    Class,
    DomainModel,
    IntegerType,
    Multiplicity,
    Property,
    StringType,
)

Theatre = Class(name="Theatre")
Show = Class(name="Show")
Reservation = Class(name="Reservation")
StandardSpectator = Class(name="StandardSpectator")
AccessibilitySpectator = Class(name="AccessibilitySpectator")

Theatre_name = Property(name="name", type=StringType)
Theatre.attributes = {Theatre_name}

Show_id = Property(name="id", type=StringType)
Show_title = Property(name="title", type=StringType)
Show_datetime = Property(name="datetime", type=StringType)
Show_price_eur = Property(name="price_eur", type=IntegerType)
Show_capacity = Property(name="capacity", type=IntegerType)
Show_pmr = Property(name="pmr_entrance", type=StringType)
Show.attributes = {
    Show_id,
    Show_title,
    Show_datetime,
    Show_price_eur,
    Show_capacity,
    Show_pmr,
}

Reservation_code = Property(name="confirmation_code", type=StringType)
Reservation_customer = Property(name="customer_name", type=StringType)
Reservation_seats = Property(name="seats", type=IntegerType)
Reservation_zone = Property(name="zone", type=StringType)
Reservation_a11y = Property(name="accessibility", type=StringType)
Reservation.attributes = {
    Reservation_code,
    Reservation_customer,
    Reservation_seats,
    Reservation_zone,
    Reservation_a11y,
}

StandardSpectator_style = Property(name="boxOfficeStyle", type=StringType)
StandardSpectator.attributes = {StandardSpectator_style}

AccessibilitySpectator_guidance = Property(name="guidance", type=StringType)
AccessibilitySpectator_tone = Property(name="boxOfficeTone", type=StringType)
AccessibilitySpectator.attributes = {
    AccessibilitySpectator_guidance,
    AccessibilitySpectator_tone,
}

theatre_shows = BinaryAssociation(
    name="programme",
    ends={
        Property(name="theatre", type=Theatre, multiplicity=Multiplicity(1, 1)),
        Property(name="shows", type=Show, multiplicity=Multiplicity(1, "*")),
    },
)

show_reservations = BinaryAssociation(
    name="bookings",
    ends={
        Property(name="show", type=Show, multiplicity=Multiplicity(1, 1)),
        Property(
            name="reservations",
            type=Reservation,
            multiplicity=Multiplicity(0, "*"),
            is_composite=True,
        ),
    },
)

spectator_reservation_std = BinaryAssociation(
    name="standard_places",
    ends={
        Property(
            name="spectator",
            type=StandardSpectator,
            multiplicity=Multiplicity(1, 1),
        ),
        Property(name="reservation", type=Reservation, multiplicity=Multiplicity(0, "*")),
    },
)

spectator_reservation_acc = BinaryAssociation(
    name="access_places",
    ends={
        Property(
            name="spectator",
            type=AccessibilitySpectator,
            multiplicity=Multiplicity(1, 1),
        ),
        Property(name="reservation", type=Reservation, multiplicity=Multiplicity(0, "*")),
    },
)

domain_model = DomainModel(
    name="Theatre_Reservation",
    types={
        Theatre,
        Show,
        Reservation,
        StandardSpectator,
        AccessibilitySpectator,
    },
    associations={
        theatre_shows,
        show_reservations,
        spectator_reservation_std,
        spectator_reservation_acc,
    },
    generalizations=set(),
)

if __name__ == "__main__":
    for cls in domain_model.get_classes():
        print(cls.name)
