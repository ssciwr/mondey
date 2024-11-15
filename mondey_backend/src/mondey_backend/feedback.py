from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import MilestoneGroup


def calculate_current_child_score(answers: dict[int, MilestoneAnswer]):
    score = 0
    for _, answer in answers.items():
        score += answer
    return score / len(answers)


def get_feedback_score(
    milestoneGroup: MilestoneGroup,
    answerssession: MilestoneAnswerSession,
    avg_stat: float,
    sigma_stat: float,
):
    avg_child = calculate_current_child_score(
        {m.id: answerssession.answers[m.id] for m in milestoneGroup.milestones}
    )

    if avg_stat - 2 * sigma_stat <= avg_child <= avg_stat - sigma_stat:
        return -1
    elif avg_stat - sigma_stat <= avg_child <= avg_stat:
        return 0
    else:
        return 1
