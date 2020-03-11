import pygame as pg

w,vw,h = 1000,1000,700
cw,ch = 107,144

pg.init()
window = pg.display.set_mode((w,h), pg.RESIZABLE|pg.HWSURFACE|pg.DOUBLEBUF)
pg.display.set_caption("Solitaire")

class Card:
	def __init__(self,rank,suit):
		self.rank = rank
		self.suit = suit
		self.faceUp = False
		self.color = False
		self.rect = pg.Rect(0,0,cw,ch)

		if suit == 0 or suit == 3:
			self.color = True

	def flip(self):
		self.faceUp = not self.faceUp

	def show(self):
		if self.faceUp:
			img = pg.image.load("cards/"+ str(self.suit)+str(self.rank) +".bmp")
		else:
			img = pg.image.load("cards/back.bmp")

		window.blit(pg.transform.scale(img.convert(), (cw,ch)), self.rect[:2])

class Pile:
	def __init__(self,h):
		self.cards = []
		self.rect = pg.Rect(0,h,cw,ch)

	def add(self,card):
		self.cards.append(card)

	def give(self,card,other):
		self.cards.remove(card)
		other.add(card)

class Game:
	def __init__(self):
		self.tableau = [Pile(ch+30) for i in range(7)]
		self.foundation = [Pile(15) for i in range(4)]
		self.stock = [Pile(15) for i in range(2)]

		for rank in range(13):
			for suit in range(4):
				self.stock[0].add(Card(rank,suit))
		import random
		random.shuffle(self.stock[0].cards)

		for i,t in enumerate(self.tableau,1):
			for x in range(i):
				self.stock[0].give(self.stock[0].cards[0],t)
			t.cards[-1].flip()

		for card in self.stock[0].cards:
			card.flip()

deal = Card(0,0)
game = Game()
undo = []

def text(text,x,y):
	window.blit(pg.font.SysFont("Consolas",36,1).render(text,False,(255,255,255)), (x,y))

def m(i):
	return pg.mouse.get_pos()[i]
def pos(v):
	return v.collidepoint(m(0),m(1))

def setdim():
	game.stock[0].rect.x = (w-vw)/2+15
	deal.rect[:2] = (w-vw)/2+15, 15

	for i,t in enumerate(game.tableau):
		fu = 0
		t.rect.x = (w-vw-cw)/2 + (2*i+1)*vw/14

		for n,x in enumerate(t.cards):
			x.rect[:2] = (w-vw-cw)/2 + (2*i+1)*vw/14, ch+30 + 10*n + 15*fu
			if x.faceUp:
				fu += 1

	for i,f in enumerate(game.foundation,1):
		f.rect.x = (w+vw)/2 - cw*i-15*i

		for x in f.cards:
			x.rect[:2] = (w+vw)/2 - cw*i-15*i, 15

	for x in game.stock[1].cards:
		x.rect[:2] = (w-vw)/2 + cw+30, 15

def show():
	def each(i,r=1):
		if r:
			pg.draw.rect(window,(25,145,95),i.rect)
		for x in i.cards:
			if x != card:
				x.show()

	window.fill((15,112,71))

	if game.stock[0].cards:
		deal.show()
	else:
		pg.draw.rect(window,(25,145,95),game.stock[0].rect)

	for t in game.tableau:
		each(t)
	for f in game.foundation:
		each(f)
	each(game.stock[1],0)

	if card and card in pile.cards:
		for i in range(pile.cards.index(card), len(pile.cards)):
			pile.cards[i].show()

	pg.display.flip()

def get(i):
	global pile,card,offset
	for x in i.cards:
		if pos(x.rect):
			pile,card = i,x
			offset = m(0)-card.rect.x, m(1)-card.rect.y

setdim()
while True:
	pile,card = None,None
	show()
	e = pg.event.wait()

	if e.type == pg.QUIT:
		break
	if e.type == pg.VIDEORESIZE:
		window = pg.display.set_mode(e.dict["size"], pg.RESIZABLE|pg.HWSURFACE|pg.DOUBLEBUF)
		w = pg.display.get_surface().get_width()
		h = pg.display.get_surface().get_height()
		setdim()
	if pg.mouse.get_pressed()[0]:
		for t in game.tableau:
			get(t)
		for f in game.foundation:
			get(f)
		get(game.stock[1])

		while (card and card.faceUp) or pos(deal.rect):
			if card:
				ind = pile.cards.index(card)
				for i in range(ind, len(pile.cards)):
					pile.cards[i].rect[:2] = m(0)-offset[0], m(1)-offset[1]+25*(i-ind)
			show()

			if pg.event.wait().type == pg.MOUSEBUTTONUP:
				for t in game.tableau:
					if t.cards:
						l = t.cards[-1]

					if (t.cards and pos(l.rect) and l.rank == card.rank+1 and l.color != card.color) or \
					(not t.cards and pos(t.rect) and card.rank == 12):
						ind = pile.cards.index(card)
						for i in range(ind, len(pile.cards)):
							pile.give(pile.cards[ind],t)

				for f in game.foundation:
					if pos(f.rect):
						if f.cards:
							l = f.cards[-1]

						if (f.cards and l.rank == card.rank-1 and l.suit == card.suit) or \
						(not f.cards and card.rank == 0):
							pile.give(card,f)

				if pos(deal.rect):
					if game.stock[0].cards:
						game.stock[0].give(game.stock[0].cards[0], game.stock[1])
					else:
						for i in range(len(game.stock[1].cards)):
							game.stock[1].give(game.stock[1].cards[0], game.stock[0])

				if pile and pile.cards and not pile.cards[-1].faceUp:
					pile.cards[-1].flip()

				setdim()
				break

pg.quit()