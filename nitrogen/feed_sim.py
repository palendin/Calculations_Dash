import numpy as np
import matplotlib.pyplot as plt

feed_rate = 5.2 # g/L/hr
feed_cap = 5.8 # g/L/hr
feed_rate1 = 5.2 # g/L/hr
feed_cap1 = 6.2 # g/L/hr
gp_feed_dose = 10 # g/L
gp_feed_pulse = 8 # number of pulses
pp_feed_dose = 15 # g/L
pp_feed_dose1 = 15 # g/L
pp_feed_pulse = 40 # number of pulses

gp_feed_increase = 2.5 # %

V0 = 125 # ml

sfeed = 726 # g/L
TRS = 56.62  # %

time = 0
total_feed = 0
feed_amount = []
total_time = []
for gpfp in range(gp_feed_pulse):
    time = time + gp_feed_dose/feed_rate
    total_feed = total_feed + feed_rate*V0/1000*(gp_feed_dose/feed_rate)
    feed_rate = feed_rate + feed_rate*gp_feed_increase/100
    feed_amount.append(total_feed)
    total_time.append(time)
    if gpfp == 7:
        for ppfp in range(pp_feed_pulse):
            time = time + pp_feed_dose/feed_cap
            total_feed = total_feed + feed_cap*V0/1000*(pp_feed_dose/feed_cap)
            feed_amount.append(total_feed)
            total_time.append(time)
time1 = 0
total_feed1 = 0
feed_amount1 = []
total_time1 = []
for gpfp in range(gp_feed_pulse):
    time1 = time1 + gp_feed_dose/feed_rate1
    total_feed1 = total_feed1 + feed_rate1*V0/1000*(gp_feed_dose/feed_rate1)
    feed_rate1 = feed_rate1 + feed_rate1*gp_feed_increase/100
    feed_amount1.append(total_feed1)
    total_time1.append(time1)
    if gpfp == 7:
        for ppfp in range(pp_feed_pulse):
            time1 = time1 + pp_feed_dose1/feed_cap1
            total_feed1 = total_feed1 + feed_cap1*V0/1000*(pp_feed_dose1/feed_cap1)
            feed_amount1.append(total_feed1)
            total_time1.append(time1)

fig, ax = plt.subplots()
plt.ylabel('feed (g)')
plt.xlabel('time (hr)')
ax.plot(total_time,feed_amount, label = 'P3')
ax.plot(total_time1,feed_amount1, label = 'P4')
ax.text(0.5, 50 , 'Blue = {:0.2f} g, Orange = {:0.2f} g'.format(feed_amount[-1], feed_amount1[-1]))
ax.legend()
plt.xticks(np.arange(0, 140, 10))
plt.show()





