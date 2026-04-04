import time

class CycleManager:
  ns_per_ms = 1000000
  
  def __init__(self, CYCLE_TIME_ms):
    self.cycle_start_ms = 0
    self.cycle_end_ms = 0
    self.total_cycle_time_ms = 0
    self.target = CYCLE_TIME_ms

  def startCycle(self):
    self.cycle_start_ms = time.monotonic_ns() / CycleManager.ns_per_ms
	
  def adjustCycle(self):
    sleep_time_ms = None
    self.cycle_end_ms = time.monotonic_ns() / CycleManager.ns_per_ms
    self.total_cycle_time_ms = self.cycle_end_ms - self.cycle_start_ms
    if self.total_cycle_time_ms < self.target:
      sleep_time_ms = self.target - self.total_cycle_time_ms
      time.sleep(sleep_time_ms / 1000)
    return self.total_cycle_time_ms, sleep_time_ms

if __name__ == "__main__":
  CYCLE_TIME_ms = 20
  ERROR_VALUE = 1
  cm = CycleManager(CYCLE_TIME_ms)

  for loop_time in [5,10,15,20,25,30]:
      cm.startCycle()
      time.sleep(loop_time / 1000)
      cycle_time_ms, sleep_time_ms = cm.adjustCycle()
      if loop_time < CYCLE_TIME_ms:
        if abs(loop_time + sleep_time_ms - CYCLE_TIME_ms) < ERROR_VALUE:
         print(loop_time, "ms test successful")
        else:
          print(loop_time, "ms test failed")
          print("   Goal:", CYCLE_TIME_ms, "ms")
          print("   Loop Time:", loop_time, "ms")
          print("   Cycle Time:", cycle_time_ms, "ms")
          print("   Correction Time:", sleep_time_ms, "ms")
          if cycle_time_ms - loop_time > ERROR_VALUE:
            print("      Cycle too long")
          elif sleep_time_ms + loop_time - CYCLE_TIME_ms > ERROR_VALUE:
            print("      Sleep too long")
          elif loop_time - cycle_time_ms > ERROR_VALUE:
            print("      Cycle too short")
          elif CYCLE_TIME_ms - loop_time - sleep_time_ms > ERROR_VALUE:
            print("      Sleep too short")
          else:
            print("      Unknown Error")
      else:
        if sleep_time_ms == None:
          print(loop_time, "ms test successful")
        else:
          print(loop_time, "ms test failed")
          print("   Goal:", CYCLE_TIME_ms, "ms")
          print("   Loop Time:", loop_time, "ms")
          print("   Cycle Time:", cycle_time_ms, "ms")
          print("   Correction Time:", sleep_time_ms, "ms")
          if cycle_time_ms - loop_time > ERROR_VALUE:
            print("      Cycle too long")
          elif sleep_time_ms != None:
            print("      Sleep too long")
          elif loop_time - cycle_time_ms > ERROR_VALUE:
            print("      Cycle too short")
          else:
            print("      Unknown Error")
