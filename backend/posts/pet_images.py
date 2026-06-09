"""
stable pet photo urls so posts and reels show a real image instead of a blank
placeholder. dog urls come from the dog.ceo cdn, cat urls from cataas. both are
permanent, hotlinkable files, no api key needed.

the seed sets a species matched url per post (a cat account gets a cat photo).
any post without one falls back to a deterministic photo by id, so the same post
always shows the same pet across the home feed and the reels feed.
"""

CAT_IMAGES = [
    "https://cataas.com/cat/04eEQhDfAL8l5nt3",
    "https://cataas.com/cat/05Xd4JtN14983pns",
    "https://cataas.com/cat/09wFxpacQzvf9jfM",
    "https://cataas.com/cat/0B2g7aTANObiqPJJ",
    "https://cataas.com/cat/0BTTVEVWXNyOgXYd",
    "https://cataas.com/cat/0C2bQ39x8kuhx31p",
    "https://cataas.com/cat/0DVs2d6bIVIt3ehk",
    "https://cataas.com/cat/0EsIYDG0at0TPpPD",
    "https://cataas.com/cat/0F0IKAPOdWiE755P",
    "https://cataas.com/cat/0GC9MRUAqxhBzPyA",
    "https://cataas.com/cat/0M0Lo3dsYft79xNd",
    "https://cataas.com/cat/0mstmOIucwiN80jb",
    "https://cataas.com/cat/0mxliw1UgtFdDkU8",
    "https://cataas.com/cat/0nnJxjVoMK6GVmRS",
]

DOG_IMAGES = [
    "https://images.dog.ceo/breeds/pug/IMG_0233.jpg",
    "https://images.dog.ceo/breeds/chihuahua/n02085620_2903.jpg",
    "https://images.dog.ceo/breeds/pointer-germanlonghair/hans2.jpg",
    "https://images.dog.ceo/breeds/danish-swedish-farmdog/ebba_003.jpg",
    "https://images.dog.ceo/breeds/spaniel-blenheim/n02086646_1733.jpg",
    "https://images.dog.ceo/breeds/terrier-scottish/n02097298_2722.jpg",
    "https://images.dog.ceo/breeds/poodle-medium/PXL_20210220_100624962.jpg",
    "https://images.dog.ceo/breeds/hound-walker/n02089867_3585.jpg",
    "https://images.dog.ceo/breeds/leonberg/n02111129_2594.jpg",
    "https://images.dog.ceo/breeds/terrier-fox/n02095314_3084.jpg",
    "https://images.dog.ceo/breeds/bluetick/n02088632_2165.jpg",
    "https://images.dog.ceo/breeds/segugio-italian/n02090722_002.jpg",
    "https://images.dog.ceo/breeds/spitz-indian/Indian_Spitz.jpg",
    "https://images.dog.ceo/breeds/bakharwal-indian/Bakharwal.jpg",
]

# alternating so a feed never shows a long run of one species
PET_IMAGES = [img for pair in zip(CAT_IMAGES, DOG_IMAGES) for img in pair]


def species_image(species: str, index: int) -> str:
    """pick a photo from the matching pool by index, wrapping around."""
    pool = DOG_IMAGES if species == "dog" else CAT_IMAGES
    return pool[index % len(pool)]


def pet_image_for(post_id: int) -> str:
    """deterministic photo for a post id, so the image is stable across feeds."""
    if not post_id:
        return PET_IMAGES[0]
    return PET_IMAGES[post_id % len(PET_IMAGES)]
