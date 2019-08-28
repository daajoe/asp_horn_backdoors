#!/usr/bin/env bash
echo $1
bzcat $1 | gringo -o smodels > $1.sm
