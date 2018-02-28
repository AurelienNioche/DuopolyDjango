from game.models import Room, Round, RoundState, RoundComposition, FirmPosition, FirmPrice, FirmProfit, \
    FirmProfitPerTurn,ConsumerChoice

from . import management


def delete(room_id):

    rm = Room.objects.filter(id=room_id).first()
    rds = Round.objects.filter(room_id=rm.id)

    for rd in rds:

        if rd:
            rs = RoundState.objects.filter(round_id=rd.id)
            rc = RoundComposition.objects.filter(round_id=rd.id)
            fpr = FirmProfit.objects.filter(round_id=rd.id)
            fpr_t = FirmProfitPerTurn.objects.filter(round_id=rd.id)
            fpc = FirmPrice.objects.filter(round_id=rd.id)
            fp = FirmPosition.objects.filter(round_id=rd.id)
            cc = ConsumerChoice.objects.filter(round_id=rd.id)

            for i in (rs, rc, fpr, fpr_t, fpc, fp, cc):
                if i.exists():
                    i.delete()

            rd.delete()

    if rm:
        rm.delete()


def create(data):
    Room.objects.select_for_update().all()
    management.create(data=data)


def get_list():
    rooms = Room.objects.all()
    return management.get_list(rooms)
