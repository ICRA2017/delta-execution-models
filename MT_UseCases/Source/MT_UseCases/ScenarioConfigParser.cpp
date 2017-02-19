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
#include "ScenarioConfigParser.h"

namespace
{
	using namespace tinyxml2;
	using std::stof;
	using std::vector;

	vector<float> ExtractMinMaxValues(string& line)
	{
		int valIdx = 0;
		while (line[valIdx] != ' ')
			valIdx++;
		float minVal = stof(line.substr(0, valIdx));

		while (line[valIdx] == ' ')
			valIdx++;
		float maxVal = stof(line.substr(valIdx, line.size() - valIdx));

		vector<float> values = { minVal, maxVal };
		return values;
	}

	void ExtractLimits(const XMLElement* limitsElement, ScenarioConfig& config)
	{
		if (limitsElement != NULL)
		{
			string xLim = limitsElement->FirstChildElement("x")->GetText();
			string yLim = limitsElement->FirstChildElement("y")->GetText();
			string zLim = limitsElement->FirstChildElement("z")->GetText();
			string rollLim = limitsElement->FirstChildElement("roll")->GetText();
			string pitchLim = limitsElement->FirstChildElement("pitch")->GetText();
			string yawLim = limitsElement->FirstChildElement("yaw")->GetText();

			vector<float> minMaxVals;
			minMaxVals = ExtractMinMaxValues(xLim);
			config.posMin.X = minMaxVals[0];
			config.posMax.X = minMaxVals[1];

			minMaxVals = ExtractMinMaxValues(yLim);
			config.posMin.Y = minMaxVals[0];
			config.posMax.Y = minMaxVals[1];

			minMaxVals = ExtractMinMaxValues(zLim);
			config.posMin.Z = minMaxVals[0];
			config.posMax.Z = minMaxVals[1];

			minMaxVals = ExtractMinMaxValues(rollLim);
			config.rotMin.X = minMaxVals[0];
			config.rotMax.X = minMaxVals[1];

			minMaxVals = ExtractMinMaxValues(pitchLim);
			config.rotMin.Y = minMaxVals[0];
			config.rotMax.Y = minMaxVals[1];

			minMaxVals = ExtractMinMaxValues(yawLim);
			config.rotMin.Z = minMaxVals[0];
			config.rotMax.Z = minMaxVals[1];
		}
	}

	void ExtractScale(const XMLElement* scaleElement, ModelConfig& config)
	{
		if (scaleElement != NULL)
		{
			config.scale.X = stof(scaleElement->FirstChildElement("x")->GetText());
			config.scale.Y = stof(scaleElement->FirstChildElement("y")->GetText());
			config.scale.Z = stof(scaleElement->FirstChildElement("z")->GetText());
		}
	}

	void ExtractPose(const XMLElement* poseElement, ModelConfig& config)
	{
		if (poseElement != NULL)
		{
			config.position.X = stof(poseElement->FirstChildElement("x")->GetText());
			config.position.Y = stof(poseElement->FirstChildElement("y")->GetText());
			config.position.Z = stof(poseElement->FirstChildElement("z")->GetText());
			config.orientation.Roll = stof(poseElement->FirstChildElement("roll")->GetText());
			config.orientation.Pitch = stof(poseElement->FirstChildElement("pitch")->GetText());
			config.orientation.Yaw = stof(poseElement->FirstChildElement("yaw")->GetText());
		}
	}

	void ExtractComOffset(const XMLElement* comOffsetElement, ModelConfig& config)
	{
		if (comOffsetElement != NULL)
		{
			config.comOffset.X = stof(comOffsetElement->FirstChildElement("x")->GetText());
			config.comOffset.Y = stof(comOffsetElement->FirstChildElement("y")->GetText());
			config.comOffset.Z = stof(comOffsetElement->FirstChildElement("z")->GetText());
		}
	}
}

ScenarioConfig ScenarioConfigParser::Load(string descriptionFile)
{
	using namespace tinyxml2;
	using std::stof;

	ScenarioConfig config;
	ModelConfig currentModel;

	XMLDocument doc;
	int fileLoadSuccess = doc.LoadFile(descriptionFile.c_str());
	if (fileLoadSuccess == XML_SUCCESS)
	{
		XMLElement* parent = doc.RootElement();
		config.type = parent->FirstChildElement("type")->GetText();

		XMLElement* limitsElement = parent->FirstChildElement("limits");
		ExtractLimits(limitsElement, config);

		XMLElement* modelsElement = parent->FirstChildElement("models");
		XMLElement* currentModelElement = modelsElement->FirstChildElement("model");
		while (currentModelElement != NULL)
		{
			currentModel.name = currentModelElement->FirstChildElement("name")->GetText();
			currentModel.type = currentModelElement->FirstChildElement("type")->GetText();
			currentModel.massScale = stof(currentModelElement->FirstChildElement("massScale")->GetText());

			string physics = currentModelElement->FirstChildElement("physics")->GetText();
			if (physics == "true")
				currentModel.simulatePhysics = true;
			else
				currentModel.simulatePhysics = false;

			ExtractScale(currentModelElement->FirstChildElement("scale"), currentModel);
			ExtractPose(currentModelElement->FirstChildElement("pose"), currentModel);
			ExtractComOffset(currentModelElement->FirstChildElement("comOffset"), currentModel);

			config.models.push_back(currentModel);
			currentModel = ModelConfig();
			currentModelElement = currentModelElement->NextSiblingElement("model");
		}
	}

	return config;
}
