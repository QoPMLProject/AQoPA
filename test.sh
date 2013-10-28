#!/bin/bash

C=1

while [ $C -eq 1 ]; do
#rm VERSION_NoNeighbour_STATES_FLOW
#rm VERSION_WithForwarders_2Hops_STATES_FLOW
#rm VERSION_WithNeighbourOnly_STATES_FLOW

python bin/aqopa-console.py -f models/wsn-join-network/model.qopml -m models/wsn-join-network/metrics.qopml -c models/wsn-join-network/versions.qopml 1> f.tmp 2> f.tmp 

R=`cat f.tmp | grep "RuntimeException"`
if [ ${#R} -gt 0 ]; then
	C=0
	cat f.tmp
fi
done

rm f.tmp
