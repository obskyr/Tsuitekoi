#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import webbrowser
import tweepy
from collections import OrderedDict

consumerKey = "aQuxitwj1dXN6CXssk1Hjd6C0"
consumerSecret = ''.join(''.join(p) for p in zip(
    "Yfa1HZmBySNrWCFsd48EO20os",
    "nmopokQCK1JnuAeeX4xxHwm7v"
))
# Yes, I am aware that this barely-even-obfuscation will stop no one who wants
# to get at the secret key and do evil things with Tsuitekoi. However, I figure
# it'll stop most maniacal GitHub bots, which I'd say is good enough.
# I don't want Tsuitekoi to depend on a server, which is the only way to really
# keep the secret "secret", but even then a simple print statement would suffice
# to break it. I just ask that you don't use the consumer secret for anything
# other than running Tsuitekoi... please? :c

class RateLimitError(Exception):
    pass

def isRateLimitError(e):
    # Tweepy doesn't provide an easy way to identify a rate limit error.
    return isinstance(e.message, list) \
        and e.message[0:] \
        and 'code' in e.message[0] \
        and e.message[0]['code'] == 88
def checkForRateLimitError(e):
    if isRateLimitError(e):
        raise RateLimitError

def handleRateLimit(cursor, handler):
    while True:
        try:
            yield cursor.next()
        except tweepy.TweepError as e:
            if not isRateLimitError(e):
                raise e
            handler()

def printRateLimitStatus(api):
    a = api.rate_limit_status()
    print "Rate limit status (method: uses/limit):"
    for method, status in (
        (
            u"/followers/ids",
            a[u"resources"][u"followers"][u"/followers/ids"],
        ),
        (
            u"/users/lookup",
            a[u"resources"][u"users"][u"/users/lookup"]
        ),
        (
            u"/application/rate_limit_status",
            a[u"resources"][u"application"][u"/application/rate_limit_status"]
        )
    ):
        print "{method}:\t{uses}/{limit}".format(
            method=method, uses=status["remaining"], limit=status["limit"]
        )
    print

def chunks(sliceable, length):
    for i in xrange(0, len(sliceable), length):
        yield sliceable[i:i + length]

class Program(object):
    def run(self):
        try:
            self.authenticate()

            # Really useful for debug, it turns out:
            # printRateLimitStatus(self.api)

            print "Loading your followers..."
            print
            self.getFollowers()

            isDifference = True
            if self.previousTime is not None:
                print "Calculating differences... We're almost done!"
                print
                self.getDifferences()

                isDifference = \
                bool([x for x in self.differences if self.differences[x]])

            if self.previousTime is not None and isDifference:
                t = time.strftime("%B %d %Y", self.previousTime)
                print "Here's what happened since {t}!".format(t=t)
                # t=t looks like one of those weird Japanese ducks.
                # It's the twitter avatar of some game dev or
                # artist, I think..? Maybe? I swear I've seen it.

                nice = {
                    "followed": "Followed you:",
                    "unfollowed": "Unfollowed you:",
                    "changedName": "Changed names:"
                }
                for differenceType in self.differences:
                    if self.differences[differenceType]:
                        print nice[differenceType]
                    for followerId, followerName in \
                    self.differences[differenceType].iteritems():
                        s = followerName
                        if differenceType == "changedName":
                            s = "{} changed name to {}".format(*followerName)
                        print '\t' + s
                    if self.differences[differenceType]:
                        # Don't want to add newlines for empty sections.
                        print
            elif not isDifference:
                t = time.strftime("%B %d %Y", self.previousTime)
                print "Nothing has happened since {t}, the last time you " \
                "ran Tsuitekoi.".format(t=t)
            else:
                print "Thanks for running Tsuitekoi for the first time!"
                print "Now you're all set to go for next time. Until then!"
                print

            self.saveFollowers()
            self.saveLog()

        except RateLimitError:
            print "Oops! It seems you've hit the rate limit for connecting" \
            "to Twitter."
            print "Try running Tsuitekoi again in 15 minutes or so!"
            print

    def getFollowers(self):
        self.previousFollowers = OrderedDict()
        try:
            with open("followers.txt", 'r') as f:
                d = f.read().strip().split('\n')
            self.previousTime = time.strptime(d[0], "%Y-%m-%d %H:%M:%S")
            for l in d[2:]:
                curId, curName = l.split(":\t")
                self.previousFollowers[int(curId)] = curName
        except IOError:
            self.previousTime = None
            pass

        def rateWait():
            print "Hit the rate limit while getting followers. You've " \
            "got a lot of"
            print "followers! Congratulations!"
            print "This means Tsuitekoi has to wait another 15 minutes " \
            "before continuing, though,"
            print "so this is going to take a while."
            print
            time.sleep(60 * 15)

        # Note: The following approach to getting followers is slightly hacky,
        # yes, but it's the most effective way to do it in regard to the rate
        # limit. Just calling tweepy.api.followers gives you up to no more than
        # 200 (one page) * 15 (rate limit) = 3000 followers per 15-minute block,
        # while this way gives you 5000 * 15 = 75,000 IDs per block and then
        # 100 * 180 = 18,000 users per block (which is the bottleneck). Sweet!

        followerIds = []
        for followerId in handleRateLimit(tweepy.Cursor(
            self.api.followers_ids,
            count=5000
        ).items(), rateWait):
            followerIds.append(followerId)

        self.followers = OrderedDict()
        for idsChunk in chunks(followerIds, 100):
            while True:
                try:
                    curUsers = self.api.lookup_users(idsChunk)
                    break
                except tweepy.TweepError as e:
                    if not isRateLimitError(e):
                        raise e
                    rateWait()

            for follower in curUsers:
                self.followers[follower.id] = follower.screen_name


    def getDifferences(self):
        self.differences = OrderedDict((
            ("followed", OrderedDict()),
            ("unfollowed", OrderedDict()),
            ("changedName", OrderedDict())
        ))

        for followerId, followerName in self.followers.iteritems():
            if followerId in self.previousFollowers:
                oldName = self.previousFollowers[followerId]
                if followerName != oldName:
                    self.differences["changedName"][followerId] = \
                    (oldName, followerName)
                del self.previousFollowers[followerId]
            else:
                self.differences["followed"][followerId] = followerName
        for followerId, followerName in self.previousFollowers.iteritems():
            self.differences["unfollowed"][followerId] = followerName

    def saveFollowers(self):
        s = time.strftime("%Y-%m-%d %H:%M:%S") + '\n\n'
        for follower in self.followers.iteritems():
            s += str(follower[0]) + ':\t' + follower[1]
            s += '\n'

        with open("followers.txt", 'w') as f:
            f.write(s)

    def saveLog(self):
        if self.previousTime is None \
        or not [x for x in self.differences if self.differences[x]]:
            return

        formats = {
            "followed": "{name} followed you.",
            "unfollowed": "{name} unfollowed you.",
            "changedName": "{oldName} changed name to {name}."
        }

        s = ""
        for differenceType in self.differences:
            formatStr = formats[differenceType]
            for followerId, followerName in \
            self.differences[differenceType].iteritems():
                oldName = None
                if differenceType == "changedName":
                    oldName = followerName[0]
                    followerName = followerName[1]

                s += formatStr.format(name=followerName, oldName=oldName) + '\n'

        with open("followlog.txt", 'a') as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S") + '\n\n')
            f.write(s)
            f.write('\n')


    def authenticate(self):
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        authPath = os.path.join(scriptDir, "auth")
        while True:
            auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
            try:
                with open(authPath, 'r') as f:
                    key, secret = f.read().split()
                    auth.set_access_token(key, secret)
                authorized = True
            except IOError:
                authorized = False

            if not authorized:
                print "You will need to authorize Tsuitekoi to access your " \
                "Twitter account."
                print "Please click \"authorize app\" in the browser window " \
                "that opens and"
                print "copy the verifier number that appears into this window."
                print

                redirectUrl = auth.get_authorization_url()
                webbrowser.open(redirectUrl)

                while auth.access_token is None:
                    verifier = raw_input("Verifier: ")
                    try:
                        auth.get_access_token(verifier)
                    except tweepy.TweepError as e:
                        print "That verifier doesn't work! Try again."
                print

                with open(authPath, 'w') as f:
                    s = auth.access_token + '\n' + auth.access_token_secret + '\n'
                    f.write(s)

            self.api = tweepy.API(auth)

            try:
                self.api.verify_credentials()
                break
            except tweepy.TweepError as e:
                checkForRateLimitError(e)
                try:
                    os.remove(authPath)
                except OSError:
                    pass
                print "There was an error authenticating your account."
                print "Please authenticate again."
                print

if __name__ == '__main__':
    tsuitekoi = Program()
    tsuitekoi.run()
