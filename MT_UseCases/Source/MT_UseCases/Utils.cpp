/**
 * Copyright 2017 by Alex Mitrevski <aleksandar.mitrevski@h-brs.de>
 *
 * This file is part of delta-execution-models.
 *
 * delta-execution-models is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * delta-execution-models is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with delta-execution-models. If not, see <http://www.gnu.org/licenses/>.
 */

#include "MT_UseCases.h"
#include "Utils.h"

bool IsPoseSame(const Pose& pose1, const Pose& pose2, double translationTolerance)
{
	const FVector& pos1 = pose1.pos;
	const FVector& pos2 = pose2.pos;
	double translationError = FVector::Dist(pos1, pos2);
	return (translationError < translationTolerance);
}

bool IsBetween(const FBox& box1, const FBox& box2, const FBox& box3, double translationTolerance)
{
	FBox leftBox;
	FBox rightBox;
	if (box2.Max.X < box3.Max.X)
	{
		leftBox = box2;
		rightBox = box3;
	}
	else
	{
		leftBox = box3;
		rightBox = box2;
	}

	return (box1.Min.X > (leftBox.Max.X - translationTolerance) &&
		box1.Max.X < (rightBox.Min.X + translationTolerance));
}

bool IsWithinBoundaries(const FBox& box1, const FBox& box2)
{
	bool xWithin = box1.Min.X > box2.Min.X && box1.Max.X < box2.Max.X;
	bool yWithin = box1.Min.X > box2.Min.X && box1.Max.X < box2.Max.X;
	return xWithin && yWithin;
}
