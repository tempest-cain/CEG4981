
            elif (car.objects.filter(licence_plate=plateNum)[0].parking_pass).expiration < datetime.datetime.now().date():