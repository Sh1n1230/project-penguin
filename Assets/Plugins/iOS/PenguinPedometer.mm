// 歩数を CoreMotion (CMPedometer) から読む。C# 側は Assets/Scripts/Systems/StepSource.cs。
// HealthKit は使わない (権限とエンタイトルメントが重いため)。端末の外には何も送らない。
#import <CoreMotion/CoreMotion.h>
#import <stdatomic.h>

static CMPedometer *penguinPedometer;
static atomic_int penguinState = 0;   // 0: 未要求, 1: 問い合わせ中, 2: 完了, 3: 失敗・許可なし
static atomic_int penguinSteps = -1;

extern "C" {

bool PenguinPedometer_IsAvailable(void)
{
    return [CMPedometer isStepCountingAvailable];
}

void PenguinPedometer_Query(double fromUnixSeconds)
{
    if (![CMPedometer isStepCountingAvailable]) {
        atomic_store(&penguinState, 3);
        return;
    }

    if (penguinPedometer == nil) {
        penguinPedometer = [[CMPedometer alloc] init];
    }

    atomic_store(&penguinState, 1);
    NSDate *from = [NSDate dateWithTimeIntervalSince1970:fromUnixSeconds];
    [penguinPedometer queryPedometerDataFromDate:from toDate:[NSDate date] withHandler:^(CMPedometerData *data, NSError *error) {
        if (error != nil || data == nil) {
            atomic_store(&penguinState, 3);
            return;
        }

        atomic_store(&penguinSteps, data.numberOfSteps.intValue);
        atomic_store(&penguinState, 2);
    }];
}

int PenguinPedometer_State(void)
{
    return atomic_load(&penguinState);
}

int PenguinPedometer_Steps(void)
{
    return atomic_load(&penguinSteps);
}

}
