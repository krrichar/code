##############################################
#   version: 0.2
#   last modified: 1/10/20
#
#   ALB client routing irule
#   This irule will be used as part of the ALB client routing (ALB phase 3) to route large (aka whale)
#   clients/requests in a way such that these large requests are spread evenly across the available
#   backend members. In other words, if there are 4 members availabe in the pool, first 4 large requests
#   should be spread across the 4 members, each serving one large request. Only then, the first member
#   that served the first large request should serve the 5th large request and so on. This may sound like
#   a round robin load balancing that tries to optimize the quickly arriving large requests so that they don't
#   end up being routed to same backend member.
#   Large Req-1 -> Member-1
#   Large Req-2 -> Member-2
#   Large Req-3 -> Member-3
#   Large Req-4 -> Member-4
#   Large Req-5 -> Member-1
#   Large Req-6 -> Member-2
##############################################
when CLIENT_ACCEPTED {
	# ALB client routing header name. Possible values are:
	#    rfb   - (really f'ing big)    - Large
	#    nbd  - (no big deal)        - Medium
	#    tayg - (that all you got) - Small
	set albCRHeaderName "x-payx-alb-payroll-rem-sz"

	set hslpool pool-high-speed-logging-splunk
    set hsl [HSL::open -proto UDP -pool $hslpool]
}

when HTTP_REQUEST {
    if { [HTTP::header exists $albCRHeaderName]  &&  [string tolower [HTTP::header $albCRHeaderName]] eq "rfb"} {

		# increment the counter for this virtual server by one
		# not sure if it is better but, don't touch mod/access dates on the entry. Use the life time
		# to reset the entry every 24 hours
        set largeReqCounter [table incr -notouch "largeReqCounter-[virtual name]"]

		# No timeout on the entry, therefore we don't touch the mod/access dates
		table timeout "largeReqCounter-[virtual name]" indef

		# 24h hard limit on lifetime on the entry 60x60x24
	    table lifetime  "largeReqCounter-[virtual name]" 86400

        set defaultPool [LB::server pool]

		# Retrieve the active members for the default pool in sorted order
        set members [lsort -index 0 [active_members -list $defaultPool]]

        # calculate the index of node relative to the list of active members by using the remainder of largeReqCounter/activeMemberCount
		set memberIndex [expr {$largeReqCounter % [active_members $defaultPool] } ]

		# payx traceability headers can be in payx_x, x-payx-, and in any mixed cases
		# when logging payx traceability headers, log them all in lower case
		set requestHeaders ""
		foreach headerName [HTTP::header names] {
			set headerNameLower [string tolower $headerName]
			if {$headerNameLower starts_with "payx_"  ||
				$headerNameLower starts_with "x-payx-" ||
				$headerNameLower equals "soapaction"} {
				append requestHeaders $headerNameLower "=" [HTTP::header value $headerName]
				append requestHeaders " , "
			}
		}

        #TimeoutLeft=[table timeout -remaining largeReqCounter-[virtual name] ] \
		#LifetimeLeft=[table lifetime -remaining largeReqCounter-[virtual name] ] \
		#Counter=$largeReqCounter \
		#TMM=[TMM::cmp_unit] \
		#ClientIP=[IP::client_addr] \

		#log local0. \
		HSL::send $hsl \
            "Source=albCR \
             RequestTime=[clock format [clock seconds] -format "%Y/%m/%d::%H:%M:%S %z"] \
             RequestURI=[HTTP::uri] \
			 SelectedNode=[lindex [lindex $members $memberIndex]  0] \
			 RequestHeaders={{$requestHeaders}}"

		# Send the traffic to the selected node
		pool $defaultPool member [lindex [lindex $members $memberIndex]  0] [lindex [lindex $members $memberIndex]  1]
    }
}
