import simpy
import tkinter
import Entities


# TODO:
# - make mutation

# ------------Environment----------
env = simpy.Environment()
# -------------CREATURES------------
food_pieces = [Entities.Food(env) for i in range(Entities.FOOD_AMOUNT)]
creatures = [Entities.Entity(env) for i in range(Entities.AMOUNT)]
Entities.Entity.set_food(food_pieces.copy())
# ----------------UI-----------------
root = tkinter.Tk()
root.title('Natural Selection')
c = tkinter.Canvas(root, width=Entities.FIELD_WIDTH, height=Entities.FIELD_HEIGHT, background='#008989')
c.pack()
entities_ui = [c.create_oval(*(creatures[i].get_canvas_location()), fill='blue') for i in range(Entities.AMOUNT)]
food_ui = [c.create_oval(*(food_pieces[i].get_canvas_location()), fill='green') for i in range(Entities.FOOD_AMOUNT)]
label = c.create_text(20, 20, text=str(Entities.AMOUNT), font='14')


def find_the_deleted_one(new, old):
    return set(set(old) - set(new))


def compare_coords(coords, to_delete):
    for item in to_delete:
        if item.get_canvas_location() == coords:
            return True
    else:
        return False


def move():
    for i in range(Entities.AMOUNT):
        env.step()

    for i in range(Entities.AMOUNT):
        c.coords(entities_ui[i], *creatures[i].get_canvas_location())

    new_food_pieces = Entities.Entity.get_food().copy()
    global food_ui, food_pieces
    if new_food_pieces != food_pieces:
        to_delete = find_the_deleted_one(new_food_pieces, food_pieces)
        food_pieces = new_food_pieces
        for oval in food_ui:
            if compare_coords(tuple([int(i) for i in c.coords(oval)]), to_delete):
                c.delete(oval)


def new_loop():
    global food_ui, food_pieces, creatures, entities_ui, label
    c.delete(tkinter.ALL)
    food_pieces = [Entities.Food(env) for i in range(Entities.FOOD_AMOUNT)]
    food_ui = [c.create_oval(*(food_pieces[i].get_canvas_location()), fill='green') for i in range(Entities.FOOD_AMOUNT)]
    Entities.Entity.set_food(food_pieces.copy())
    creatures = list(filter(lambda cr: True if cr.food_consumed else False, creatures))  # kill the weak ones
    babies = list(map(lambda cr: cr.breed(), filter(lambda cr: True if cr.food_consumed == 2 else False, creatures)))  # breed
    babies = list(filter(lambda cr: False if cr is None else True, babies))
    for creature in creatures:  # reset creatures
        creature.reset()
    creatures.extend(babies)
    Entities.AMOUNT = len(creatures)
    c.delete(label)
    num_of_mutation = len(list(filter(lambda cr: cr.mutation, creatures)))
    label = c.create_text(100, 20, text=str(Entities.AMOUNT)+', mutated: '+str(round(100/Entities.AMOUNT*num_of_mutation))+'%', font='14')
    entities_ui = [c.create_oval(*(creatures[i].get_canvas_location()), fill='red' if creatures[i].mutation else 'blue') for i in range(Entities.AMOUNT)]
    params = [0, 0, 0]
    for i in range(Entities.AMOUNT):
        for j in range(len(params)):
            params[j] += creatures[i].params()[j]
    params = [i / Entities.AMOUNT for i in params]
    print('avg. speed: {:.2f}, avg. dist: {:.2f}, avg. range: {:.2f}'.format(*params))


def main():
    move()
    for creature in creatures:
        if not creature.done:
            break
    else:
        new_loop()
    root.after(Entities.FRAMERATE, main)


main()
root.mainloop()


