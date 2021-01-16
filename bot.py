import random
import os
import csv
from tempfile import NamedTemporaryFile
from config import *
from tlasky_insta import *
from traceback import print_exc
from datetime import datetime, timedelta

session_file = './session.pickle'
if os.path.isfile(session_file):
    os.remove(session_file)

loader = Instaloader()
safe_login(
    loader,
    username, password,
    session_path
)
insta = TlaskyInsta(loader)


def process_notifications():
    # Process notifications
    print('Checking notifications.')
    for notification in insta.get_notifications():
        if insta.last_notifications_at < notification.at:
            # Process comments and comments mentions
            if notification.type in (NotificationType.COMMENT, NotificationType.COMMENT_MENTION):
                post = notification.get_media(loader.context)
                for comment in post.get_comments():
                    if comment.text == notification.text:
                        insta.like_comment(comment)
    insta.mark_notifications()


def load_posts() -> List[Post]:
    print('Loading posts.')
    global interests
    # Set because we don't want duplicated posts
    posts = set()
    random.shuffle(interests)
    for item in interests:
        posts.update(iterlist(
            loader.get_location_posts(item) if type(item) == int else loader.get_hashtag_posts(item),
            random.randint(5, 10)
        ))
        wait(random.uniform(1, 2))
        #wait(random.uniform(60, 60 * 2))
    # List because we can shuffle it
    posts = list(posts)
    random.shuffle(posts)
    return posts

# csv file with followers list
filename = 'followers.csv'
tempfile = NamedTemporaryFile(mode='w', delete=False)
fields = ['username','timestamp']

#Counter
followed = 0
likes = 0

while True:
    try:
        # Have a pause over night
        if not 7 < datetime.now().hour <= 23:
            time.sleep(0.5)
        else:
            # Check notifications (to set notifications_at)
            if not insta.last_notifications_at:
                process_notifications()
            # Like posts
            for post in load_posts():
                profile = post.owner_profile
                followers = profile.followers
                print(f"profile:",profile,"followers:",followers)
                if followers < 800:
                    print('Liking ', f'https://instagram.com/p/{post.shortcode}', 'of', profile.username)
                    likes += 1
                    if not insta.like_post(post).viewer_has_liked:
                        # Confirm that image was really liked
                        print(f'Liking is probably blocked. Please delete "{session_path}" and re-login.')

                     # Follow the user
                    if not profile.followed_by_viewer:
                        print(f"Following",profile.username,'timestamp:' , datetime.now().strftime("%d/%m/%Y %H:%M:%S")+"\n")
                        insta.follow_profile(profile)
                        with open('followers.csv','a') as fd:
                            myCsvRow= str(profile.username)+","+str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))+"\n"
                            fd.write(myCsvRow)
                            followed += 1
                else:
                    print(f"User",profile.username,'has too much followers:',followers,"\n")

                # Process notifications at least every ~ 20+ minutes
                if datetime.now() - insta.last_notifications_at > timedelta(minutes=20):
                    process_notifications()
                # Wait to avoid rate limit or likes block
                wait(random.uniform(1, 1))
                #wait(random.uniform(60 * 20, 60 * 30))
    except (
            KeyboardInterrupt,
            LoginRequiredException, TwoFactorAuthRequiredException,
            ConnectionException, BadCredentialsException, InvalidArgumentException
    ):
        print("\n\n"+f"Report:")
        print('Liked {} photos.'.format(likes))
        print('Followed {} new people.'.format(followed)+"\n")
        break
    except Exception:
        print_exc()
        if debug:
            break
