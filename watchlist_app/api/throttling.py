from rest_framework.throttling import UserRateThrottle

class ReviewCreateThrottle(UserRateThrottle):
    scope = "review-cerate"


class ReviewListThrottle(UserRateThrottle):
    scope = "review-list"
