# Zomato KPT Prediction - Multi-Signal Approach

This repository contains the simulation code for improving Kitchen Prep Time (KPT) prediction at Zomato through signal quality improvements.

## Problem Statement

Current KPT models suffer from label contamination where merchant FOR (Food Order Ready) marks are influenced by rider arrival, creating circular dependencies in predictions.

## Our Solution

Three-layer signal stack:
1. Behavioral fixes (zero cost)
2. Multi-signal rush detection
3. Tiered IoT deployment

## Results

- 47% reduction in rider wait time
- 41% improvement in P50 ETA error
- 45% improvement in P90 ETA error
- 90x ROI in Year 1

## Repository Structure