import random


def quotes_processor(request):
    quotes = [
        "<em>Hosting the Oscars is pretty much the scariest thing you can do. To me, this is right up there with bungee jumping!</em><br>&mdash; Ellen DeGeneres",
        "<em>Overall, we've lost risk-takers on the red carpet at the Academy Awards. All too often, stars play it safe.</em><br>&mdash; Brad Goreski",
        "<em>At the Academy Awards every year, there are best-dressed stars - and worst-dressed stars. But it's the worst-dressed that go down in history.</em><br>&mdash; Brad Goreski",
        "<em>I didn't get into film to win Academy Awards. I wanted to have a conversation with the audience.</em><br>&mdash; Kevin Smith",
        "<em>I went to a couple Academy Awards parties and I was definitely like, 'Whoa, no one will talk to me.'</em><br>&mdash; Matt Stone",
        "<em>Oh yeah, I'm about to host the Genies, which are the Canadian Academy Awards.</em><br>&mdash; Andrea Martin",
        "<em>I'm officially retired as the refuser of Academy Awards.</em><br>&mdash; Sacheen Littlefeather",
        "<em>I know the Academy Awards are all about the art, and love, of movie making. But I have to say, my favorite part is the dresses! Ashlan</em><br>&mdash; Gorse Cousteau",
        "<em>I'm thrilled to be asked to host the Academy Awards for the second time because, as they say, the third time's a charm.</em><br>&mdash; Jon Stewart",
        "<em>I want everybody who is watching to come to the Academy Awards with us. I'm going to pay for the bus.</em><br>&mdash; Steven Cojocaru",
        "<em>Welcome to the 77th and last Oscars.</em><br>&mdash; Chris Rock",
        "<em>Hosting the Oscars is much like making love to a woman. It's something I only get to do when Billy Crystal is out of town.</em><br>&mdash; Steve Martin",
        "<em>I think that if you go about making movies to win Oscars, you're really going about it the wrong way.</em><br>&mdash; Nicolas Cage",
        "<em>I took the Oscars very seriously as a child.</em><br>&mdash; Billy Eichner",
        "<em>If I messed up at the Oscars, I wouldn't be invited back.</em><br>&mdash; Ansel Elgort",
        "<em>People that watch Adult Swim don't watch the Oscars.</em><br>&mdash; T-Pain",
        "<em>A guy once told me that I sound like I'm a little ahead of myself. I can't wait to thank him at the Oscars. </em><br>&mdash; Nicole Ari Parker",
    ]

    return {"quote": random.choice(quotes)}
