#import <Foundation/Foundation.h>
#import <WatchConnectivity/WatchConnectivity.h>

@interface OrchidWatchBridge : NSObject <WCSessionDelegate>
+ (instancetype)shared;
- (void)start;
- (void)publishSpeaker:(NSString *)speaker dialogue:(NSString *)dialogue choices:(NSArray<NSString *> *)choices;
@end

@implementation OrchidWatchBridge
+ (instancetype)shared { static id x; static dispatch_once_t once; dispatch_once(&once, ^{ x=[self new]; }); return x; }
- (void)start {
    if (![WCSession isSupported]) return;
    WCSession *s=WCSession.defaultSession; s.delegate=self; [s activateSession];
}
- (void)publishSpeaker:(NSString *)speaker dialogue:(NSString *)dialogue choices:(NSArray<NSString *> *)choices {
    WCSession *s=WCSession.defaultSession;
    NSDictionary *m=@{@"speaker":speaker?:@"",@"dialogue":dialogue?:@"",@"choices":choices?:@[]};
    NSError *e=nil; [s updateApplicationContext:m error:&e];
    if (s.reachable) [s sendMessage:m replyHandler:nil errorHandler:nil];
}
- (void)session:(WCSession *)session activationDidCompleteWithState:(WCSessionActivationState)state error:(NSError *)error {}
- (void)sessionDidBecomeInactive:(WCSession *)session {}
- (void)sessionDidDeactivate:(WCSession *)session { [session activateSession]; }
- (void)session:(WCSession *)session didReceiveMessage:(NSDictionary<NSString *,id> *)message {
    NSString *cmd=message[@"command"]; NSNumber *idx=message[@"index"];
    [[NSNotificationCenter defaultCenter] postNotificationName:@"OrchidWatchCommand"
                                                        object:nil
                                                      userInfo:@{@"command":cmd?:@"",@"index":idx?:@(-1)}];
}
@end
