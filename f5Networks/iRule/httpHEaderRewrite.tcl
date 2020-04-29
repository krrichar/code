# iRule Checks if requested host equals *.somedomain.com (chat base URLs) then
# replaces the host header value with myservices.somedomain.com/api/

when HTTP_REQUEST {
# High speed logging
    set hslpool pool-high-speed-logging-splunk
    set hsl [HSL::open -proto UDP -pool $hslpool]

   if {[HTTP::host] starts_with "chat.somedomain.com"} {
	  HTTP::header replace Host "myservices.somedomain.com"
	  HTTP::uri "/api/chat"

    HSL::send $hsl "nonprodchat.somedomain.com replaced with myservices.somedomain.com/api/chat"
   }
   elseif {[HTTP::host] starts_with "nonprodchat.somedomain.com"} {
	  HTTP::header replace Host "myservices.somedomain.com"
	  HTTP::uri "/api/nonprodchat"

    HSL::send $hsl "nonprodchat.somedomain.com replaced with myservices.somedomain.com/api/noprodchat"
	}
	elseif {[HTTP::host] starts_with "hrchat.somedomain.com"} {
	  HTTP::header replace Host "myservices.somedomain.com"
	  HTTP::uri "/api/hrchat"

	HSL::send $hsl "hrchat.somedomain.com replaced with myservices.somedomain.com/api/hrchat"
	}
	elseif {[HTTP::host] starts_with "nonprodhrchat.somedomain.com"} {
	  HTTP::header replace Host "myservices.somedomain.com"
	  HTTP::uri "/api/nonprodhrchat"

   	HSL::send $hsl "nonprodhrchat.somedomain.com replaced with myservices.somedomain.com/api/nonprodhrchat"
	}
}
