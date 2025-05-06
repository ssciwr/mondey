-- user account with password: user
INSERT INTO user VALUES(1,0,0,0,'user@mondey.de','$argon2id$v=19$m=65536,t=3,p=4$GvhFeRAUuFTIPGWwuvFxZw$FhxMaePdtj8SpeTsYrdUKt98AHUjI++kIG+d5Cw+gSg',1,0,1);

-- researcher account with password: researcher
INSERT INTO user VALUES(2,1,1,0,'researcher@mondey.de','$argon2id$v=19$m=65536,t=3,p=4$xXDRwvE1B0W+0t8iMfXUFw$IvWrgpuKseVngtqIlX3mzhakHzd/A8kOUOQnHztTjF8',1,0,1);

-- admin account with password: admin
INSERT INTO user VALUES(3,1,1,0,'admin@mondey.de','$argon2id$v=19$m=65536,t=3,p=4$pxRfTWVoh0bmdaoSsFRztQ$xhd7vQTN5gtSkGZ+/0P5O1PhAXJe050T68/0gy23pls',1,1,1);
