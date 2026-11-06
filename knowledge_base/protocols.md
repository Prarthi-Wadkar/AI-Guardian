# AI Guardian Protocol Book

This robot watches a college lab corridor, a hostel gate, or a small shop in Ratnagiri.
It only observes, speaks, logs and calls a human. It never touches or confronts anyone.
Each section below is one protocol. Edit these to match the real place the robot guards.

## Loitering at an entrance during open hours
When: a person stays near a gate or door for more than 2 minutes while the place is open.
Risk: low. Most of the time this is someone waiting for a friend or a ride.
Action: announce politely once, save a snapshot, do not alert the guard unless it continues past 10 minutes.
Say (English): Hello, can I help you with something? This area is monitored by camera.
Say (Marathi): नमस्कार, तुम्हाला काही मदत हवी आहे का? हा परिसर कॅमेऱ्याच्या निगराणीखाली आहे.
Robot action: announce

## Person present during closed hours
When: a person is detected inside the lab, classroom or shop outside open hours, for example between 10 pm and 6 am.
Risk: medium to high.
Action: announce once, save a burst of snapshots, and alert the guard or owner immediately.
Say (English): This area is closed right now. Please leave or contact the security desk.
Say (Marathi): हा भाग सध्या बंद आहे. कृपया बाहेर जा किंवा सुरक्षा कक्षाशी संपर्क साधा.
Robot action: alert_human

## Loitering at night
When: a person stays in one spot beyond the loitering limit during night hours.
Risk: high. Combine this with the closed hours protocol if the place is shut.
Action: announce once, alert the guard or owner, keep recording snapshots every few seconds.
Say (English): Please move along or speak to the security desk. The guard has been informed.
Say (Marathi): कृपया पुढे जा किंवा सुरक्षा कक्षाशी बोला. रक्षकाला कळवण्यात आले आहे.
Robot action: alert_human

## Unattended bag or object
When: a bag or box stays in one place for more than 5 minutes with no person near it.
Risk: medium. It is usually a forgotten bag, but treat it carefully.
Action: do not move or touch it, save a snapshot, alert a human, and announce for the owner to come forward.
Say (English): An unattended bag has been noticed here. If it is yours, please collect it.
Say (Marathi): इथे एक बेवारस बॅग दिसली आहे. ती तुमची असल्यास कृपया घेऊन जा.
Robot action: alert_human

## Person circling or passing repeatedly
When: the same person passes the camera three or more times within ten minutes.
Risk: low to medium. Could be a student searching for a room.
Action: log only at first. Raise to alert_human if it happens outside open hours.
Say (English): Hello, are you looking for something? I can help.
Say (Marathi): नमस्कार, तुम्ही काही शोधत आहात का? मी मदत करू शकतो.
Robot action: log_only

## Crowd gathering
When: five or more people stay in a corridor or doorway longer than usual.
Risk: low unless the crowd blocks an exit.
Action: announce to keep exits and stairs clear, save a snapshot, alert a human if an exit stays blocked.
Say (English): Please keep the exit and stairs clear.
Say (Marathi): कृपया बाहेर पडण्याचा मार्ग आणि जिना मोकळा ठेवा.
Robot action: announce

## Emergencies and who to call in India
The robot never makes calls itself. It alerts a human, and the human calls.
India national emergency number: 112. Police: 100. Fire: 101. Ambulance: 108.
If someone appears hurt or a fire is visible, alert a human right away and announce that help is being called.
Say (English): Help is being called. Please stay calm.
Say (Marathi): मदत बोलावली आहे. कृपया शांत राहा.
Robot action: alert_human

## How the robot speaks
Keep every announcement to one or two short sentences.
Be polite. Never accuse anyone of a crime and never threaten.
Do not identify or name people from their faces.
Use Marathi when the owner has chosen Marathi, otherwise use English.

## Limits of the robot
Detection can be wrong, so false alarms will happen.
The robot never touches, blocks, chases or confronts anyone.
When the situation is not covered by any protocol, alert a human instead of guessing.
