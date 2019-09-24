#!/usr/bin/env perl


print "start server\n";
while(1){
	system('/usr/bin/env python web.py');
	sleep(5);
	print "restart server\n";
}
