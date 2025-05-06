from enum import Enum
import json

class Goal(Enum):
    """An enumeration representing the different types of goals a Criteria can have."""

    NONE = 0
    MAXIMIZE = 1
    MINIMIZE = 2
    TARGET = 3
    IN_RANGE = 4
    EQUAL_TO = 5
    CPK = 6

    def __str__(self):
        return self.name


class Optimizer:
    """The Optimizer class is used to set criteria on one or more Analyses,
    then use those criteria to find the optimal parameters.
    """

    def __init__(self, client):
        self.__client = client

        result = self.__client.send_payload({
            "method": "GET",
            "uri": "optimizer",
        })

        self.__criteria = []
        self.__solutions = tuple()

    def __str__(self):
        out = ''
        for c in self.__criteria:
            if c.goal != Goal.NONE:
                out += '{}\n'.format(c)
        out += "Found {} solutions:".format(len(self.__solutions))
        for s in self.__solutions:
            out += '{}\n'.format(s)
        return out

    def have_criteria(self):
        for c in self.__criteria:
            if c.factor and c.goal == Goal.NONE:
                return False
        return True

    def add_criteria(self, criteria):
        if criteria.factor and criteria.goal == Goal.NONE:
            raise ValueError("Can't add criteria - no goal specified for '{}'.".format(criteria.name))
        if criteria.restrict_discrete==True:
            if not criteria.factor:
                raise ValueError("Can't add criteria - It is not a discrete factor. For response/analysis '{}', restrict_discrete must be False.".format(criteria.name))
            if (criteria.factor.type != "Numeric") or (criteria.factor.type == "Numeric" and criteria.factor.subtype != "Discrete"):
                raise ValueError("Can't add criteria - It is not a discrete factor. For factor '{}', restrict_discrete must be False.".format(criteria.name))
        self.__criteria.append(criteria)

    @property
    def solutions(self):
        return self.__solutions

    def optimize(self):
        """ Runs the optimization routine. Must have one or more Criteria specified. """

        if not self.have_criteria():
            raise ValueError("Can't run optimization - no criteria specified!")

        result = self.__client.send_payload({
            "method": "POST",
            "uri": "optimizer",
            "criteria": [ c.to_dict() for c in self.__criteria ],
        })
        solutions = []
        for solution in result['payload']['solutions']:
            solutions.append(json.loads(solution))
        self.__solutions = tuple(solutions)


class Criteria:
    """The Criteria class is used by the optimizer to calculate a desirability score
    for a given point in the design space, which is then used to search for an optimal point.

    Each Analysis and Factor can have a Criteria (e.g. you might maximize the output of an Analysis,
    and target a certain value of a Factor).
    """

    def __init__(self, factor=None, analysis=None):
        """ Create a Criteria for a Factor or Analysis. """

        if (not analysis and not factor) or (analysis and factor):
            raise ValueError("You must pass in either an analysis or factor.")

        self.__analysis = analysis
        self.__factor = factor

        self.__name = ''
        self.__goal = Goal.NONE
        self.__target = 0
        self.__lower_limit = 0
        self.__upper_limit = 0
        self.__lower_weight = 1
        self.__upper_weight = 1
        self.__importance = 0
        self.__restrict_discrete = False

    def __str__(self):
        name = ''
        if self.__analysis:
            name += self.__analysis.name
        if self.__factor:
            name += self.__factor.name
        result = "Criteria for {} -> Goal: {} Target: {} Lower Limit: {} Upper Limit: {} Lower Weight: {} Upper Weight: {} Importance: {} Restrict discrete: {}".format(
            name,
            self.__goal,
            self.__target,
            self.__lower_limit,
            self.__upper_limit,
            self.__lower_weight,
            self.__upper_weight,
            self.__importance,
            self.__restrict_discrete,
        )
        if self.__factor:
            result += " " + "Restrict discrete: "+ str(self.__restrict_discrete)
        return result

    @property
    def name(self):
        """ The name of this Criteria (analysis/response or factor name). """
        if self.__analysis:
            self.__name = self.__analysis.name
        elif self.__factor:
            self.__name = self.__factor.name
        else:
            raise ValueError("You must pass in either an analysis or factor.")
        return self.__name

    @property
    def goal(self):
        """ The goal of this Criteria (e.g. Goal.MAXIMIZE). """
        return self.__goal

    @goal.setter
    def goal(self, goal):
        self.__goal = goal

    @property
    def target(self):
        """ The target for this Criteria, if using Goal.EQUAL_TO or Goal.TARGET """
        return self.__target

    @target.setter
    def target(self, target):
        self.__target = target

    @property
    def lower_limit(self):
        """ The lower limit for this Criteria. """
        return self.__lower_limit

    @lower_limit.setter
    def lower_limit(self, lower_limit):
        self.__lower_limit = lower_limit

    @property
    def upper_limit(self):
        """ The upper limit for this Criteria. """
        return self.__upper_limit

    @upper_limit.setter
    def upper_limit(self, upper_limit):
        self.__upper_limit = upper_limit

    @property
    def lower_weight(self):
        """ The lower weight for this Criteria. """
        return self.__lower_weight

    @lower_weight.setter
    def lower_weight(self, lower_weight):
        self.__lower_weight = lower_weight

    @property
    def upper_weight(self):
        """ The upper weight for this Criteria. """
        return self.__upper_weight

    @upper_weight.setter
    def upper_weight(self, upper_weight):
        self.__upper_weight = upper_weight

    @property
    def importance(self):
        """ The importance of this Criteria, relative to other Criteria. """
        return self.__importance

    @importance.setter
    def importance(self, importance):
        self.__importance = importance

    @property
    def restrict_discrete(self):
        """ The restrict discrete for this Criteria. """
        return self.__restrict_discrete

    @property
    def factor(self):
        return self.__factor

    @restrict_discrete.setter
    def restrict_discrete(self, restrict_discrete):
        self.__restrict_discrete = restrict_discrete

    def to_dict(self):
        out_dict = {
            'analysis': self.__analysis.name if self.__analysis else None,
            'factor': self.__factor.name if self.__factor else None,
            'goal': str(self.__goal),
        }

        # the rest of the members are primitives
        for k, v in self.__dict__.items():
            key = k[11:] # strip off leading 'Criteria__'
            if key in out_dict.keys():
                continue
            out_dict[key] = v
        return out_dict

