// This file is auto-generated by @hey-api/openapi-ts

import { createClient, createConfig, type Options, formDataBodySerializer, urlSearchParamsBodySerializer } from '@hey-api/client-fetch';
import type { GetLanguagesError, GetLanguagesResponse, GetMilestonesError, GetMilestonesResponse, GetMilestoneData, GetMilestoneError, GetMilestoneResponse, GetMilestoneGroupsData, GetMilestoneGroupsError, GetMilestoneGroupsResponse, SubmitMilestoneImageData, SubmitMilestoneImageError, SubmitMilestoneImageResponse, GetUserQuestionsError, GetUserQuestionsResponse, GetChildQuestionsError, GetChildQuestionsResponse, CreateLanguageData, CreateLanguageError, CreateLanguageResponse, DeleteLanguageData, DeleteLanguageError, DeleteLanguageResponse, UpdateI18NData, UpdateI18NError, UpdateI18NResponse, GetMilestoneGroupsAdminError, GetMilestoneGroupsAdminResponse, CreateMilestoneGroupAdminError, CreateMilestoneGroupAdminResponse, UpdateMilestoneGroupAdminData, UpdateMilestoneGroupAdminError, UpdateMilestoneGroupAdminResponse, DeleteMilestoneGroupAdminData, DeleteMilestoneGroupAdminError, DeleteMilestoneGroupAdminResponse, OrderMilestoneGroupsAdminData, OrderMilestoneGroupsAdminError, OrderMilestoneGroupsAdminResponse, UploadMilestoneGroupImageData, UploadMilestoneGroupImageError, UploadMilestoneGroupImageResponse, CreateMilestoneData, CreateMilestoneError, CreateMilestoneResponse, UpdateMilestoneData, UpdateMilestoneError, UpdateMilestoneResponse, DeleteMilestoneData, DeleteMilestoneError, DeleteMilestoneResponse, OrderMilestonesAdminData, OrderMilestonesAdminError, OrderMilestonesAdminResponse, UploadMilestoneImageData, UploadMilestoneImageError, UploadMilestoneImageResponse, DeleteMilestoneImageData, DeleteMilestoneImageError, DeleteMilestoneImageResponse, GetSubmittedMilestoneImagesError, GetSubmittedMilestoneImagesResponse, ApproveSubmittedMilestoneImageData, ApproveSubmittedMilestoneImageError, ApproveSubmittedMilestoneImageResponse, DeleteSubmittedMilestoneImageData, DeleteSubmittedMilestoneImageError, DeleteSubmittedMilestoneImageResponse, GetMilestoneAgeScoresData, GetMilestoneAgeScoresError, GetMilestoneAgeScoresResponse, GetUserQuestionsAdminError, GetUserQuestionsAdminResponse, UpdateUserQuestionData, UpdateUserQuestionError, UpdateUserQuestionResponse, CreateUserQuestionError, CreateUserQuestionResponse, DeleteUserQuestionData, DeleteUserQuestionError, DeleteUserQuestionResponse, OrderUserQuestionsAdminData, OrderUserQuestionsAdminError, OrderUserQuestionsAdminResponse, GetChildQuestionsAdminError, GetChildQuestionsAdminResponse, UpdateChildQuestionData, UpdateChildQuestionError, UpdateChildQuestionResponse, CreateChildQuestionError, CreateChildQuestionResponse, DeleteChildQuestionData, DeleteChildQuestionError, DeleteChildQuestionResponse, OrderChildQuestionsAdminData, OrderChildQuestionsAdminError, OrderChildQuestionsAdminResponse, GetUsersError, GetUsersResponse, GetResearchGroupsError, GetResearchGroupsResponse, CreateResearchGroupData, CreateResearchGroupError, CreateResearchGroupResponse, DeleteResearchGroupData, DeleteResearchGroupError, DeleteResearchGroupResponse, UsersCurrentUserError, UsersCurrentUserResponse, UsersPatchCurrentUserData, UsersPatchCurrentUserError, UsersPatchCurrentUserResponse, UsersUserData, UsersUserError, UsersUserResponse, UsersPatchUserData, UsersPatchUserError, UsersPatchUserResponse, UsersDeleteUserData, UsersDeleteUserError, UsersDeleteUserResponse, GetChildrenError, GetChildrenResponse, UpdateChildData, UpdateChildError, UpdateChildResponse, CreateChildData, CreateChildError, CreateChildResponse, GetChildData, GetChildError, GetChildResponse, DeleteChildData, DeleteChildError, DeleteChildResponse, GetChildImageData, GetChildImageError, GetChildImageResponse, UploadChildImageData, UploadChildImageError, UploadChildImageResponse, DeleteChildImageData, DeleteChildImageError, DeleteChildImageResponse, GetCurrentMilestoneAnswerSessionData, GetCurrentMilestoneAnswerSessionError, GetCurrentMilestoneAnswerSessionResponse, UpdateMilestoneAnswerData, UpdateMilestoneAnswerError, UpdateMilestoneAnswerResponse, GetCurrentUserAnswersError, GetCurrentUserAnswersResponse, UpdateCurrentUserAnswersData, UpdateCurrentUserAnswersError, UpdateCurrentUserAnswersResponse, GetCurrentChildAnswersData, GetCurrentChildAnswersError, GetCurrentChildAnswersResponse, UpdateCurrentChildAnswersData, UpdateCurrentChildAnswersError, UpdateCurrentChildAnswersResponse, GetMilestoneAnswerSessionsInStatisticsData, GetMilestoneAnswerSessionsInStatisticsError, GetMilestoneAnswerSessionsInStatisticsResponse, GetMilestonegroupsForSessionData, GetMilestonegroupsForSessionError, GetMilestonegroupsForSessionResponse, GetSummaryFeedbackForAnswersessionData, GetSummaryFeedbackForAnswersessionError, GetSummaryFeedbackForAnswersessionResponse, GetDetailedFeedbackForAnswersessionData, GetDetailedFeedbackForAnswersessionError, GetDetailedFeedbackForAnswersessionResponse, AuthCookieLoginData, AuthCookieLoginError, AuthCookieLoginResponse, AuthCookieLogoutError, AuthCookieLogoutResponse, RegisterRegisterData, RegisterRegisterError, RegisterRegisterResponse, ResetForgotPasswordData, ResetForgotPasswordError, ResetForgotPasswordResponse, ResetResetPasswordData, ResetResetPasswordError, ResetResetPasswordResponse, VerifyRequestTokenData, VerifyRequestTokenError, VerifyRequestTokenResponse, VerifyVerifyData, VerifyVerifyError, VerifyVerifyResponse, AuthError, AuthResponse } from './types.gen';

export const client = createClient(createConfig());

/**
 * Get Languages
 */
export const getLanguages = <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<GetLanguagesResponse, GetLanguagesError, ThrowOnError>({
        ...options,
        url: '/languages/'
    });
};

/**
 * Get Milestones
 */
export const getMilestones = <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<GetMilestonesResponse, GetMilestonesError, ThrowOnError>({
        ...options,
        url: '/milestones/'
    });
};

/**
 * Get Milestone
 */
export const getMilestone = <ThrowOnError extends boolean = false>(options: Options<GetMilestoneData, ThrowOnError>) => {
    return (options?.client ?? client).get<GetMilestoneResponse, GetMilestoneError, ThrowOnError>({
        ...options,
        url: '/milestones/{milestone_id}'
    });
};

/**
 * Get Milestone Groups
 */
export const getMilestoneGroups = <ThrowOnError extends boolean = false>(options: Options<GetMilestoneGroupsData, ThrowOnError>) => {
    return (options?.client ?? client).get<GetMilestoneGroupsResponse, GetMilestoneGroupsError, ThrowOnError>({
        ...options,
        url: '/milestone-groups/{child_id}'
    });
};

/**
 * Submit Milestone Image
 */
export const submitMilestoneImage = <ThrowOnError extends boolean = false>(options: Options<SubmitMilestoneImageData, ThrowOnError>) => {
    return (options?.client ?? client).post<SubmitMilestoneImageResponse, SubmitMilestoneImageError, ThrowOnError>({
        ...options,
        ...formDataBodySerializer,
        headers: {
            'Content-Type': null,
            ...options?.headers
        },
        url: '/submitted-milestone-images/{milestone_id}'
    });
};

/**
 * Get User Questions
 */
export const getUserQuestions = <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<GetUserQuestionsResponse, GetUserQuestionsError, ThrowOnError>({
        ...options,
        url: '/user-questions/'
    });
};

/**
 * Get Child Questions
 */
export const getChildQuestions = <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<GetChildQuestionsResponse, GetChildQuestionsError, ThrowOnError>({
        ...options,
        url: '/child-questions/'
    });
};

/**
 * Create Language
 */
export const createLanguage = <ThrowOnError extends boolean = false>(options: Options<CreateLanguageData, ThrowOnError>) => {
    return (options?.client ?? client).post<CreateLanguageResponse, CreateLanguageError, ThrowOnError>({
        ...options,
        url: '/admin/languages/'
    });
};

/**
 * Delete Language
 */
export const deleteLanguage = <ThrowOnError extends boolean = false>(options: Options<DeleteLanguageData, ThrowOnError>) => {
    return (options?.client ?? client).delete<DeleteLanguageResponse, DeleteLanguageError, ThrowOnError>({
        ...options,
        url: '/admin/languages/{language_id}'
    });
};

/**
 * Update I18N
 */
export const updateI18N = <ThrowOnError extends boolean = false>(options: Options<UpdateI18NData, ThrowOnError>) => {
    return (options?.client ?? client).put<UpdateI18NResponse, UpdateI18NError, ThrowOnError>({
        ...options,
        url: '/admin/i18n/{language_id}'
    });
};

/**
 * Get Milestone Groups Admin
 */
export const getMilestoneGroupsAdmin = <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<GetMilestoneGroupsAdminResponse, GetMilestoneGroupsAdminError, ThrowOnError>({
        ...options,
        url: '/admin/milestone-groups/'
    });
};

/**
 * Create Milestone Group Admin
 */
export const createMilestoneGroupAdmin = <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => {
    return (options?.client ?? client).post<CreateMilestoneGroupAdminResponse, CreateMilestoneGroupAdminError, ThrowOnError>({
        ...options,
        url: '/admin/milestone-groups/'
    });
};

/**
 * Update Milestone Group Admin
 */
export const updateMilestoneGroupAdmin = <ThrowOnError extends boolean = false>(options: Options<UpdateMilestoneGroupAdminData, ThrowOnError>) => {
    return (options?.client ?? client).put<UpdateMilestoneGroupAdminResponse, UpdateMilestoneGroupAdminError, ThrowOnError>({
        ...options,
        url: '/admin/milestone-groups'
    });
};

/**
 * Delete Milestone Group Admin
 */
export const deleteMilestoneGroupAdmin = <ThrowOnError extends boolean = false>(options: Options<DeleteMilestoneGroupAdminData, ThrowOnError>) => {
    return (options?.client ?? client).delete<DeleteMilestoneGroupAdminResponse, DeleteMilestoneGroupAdminError, ThrowOnError>({
        ...options,
        url: '/admin/milestone-groups/{milestone_group_id}'
    });
};

/**
 * Order Milestone Groups Admin
 */
export const orderMilestoneGroupsAdmin = <ThrowOnError extends boolean = false>(options: Options<OrderMilestoneGroupsAdminData, ThrowOnError>) => {
    return (options?.client ?? client).post<OrderMilestoneGroupsAdminResponse, OrderMilestoneGroupsAdminError, ThrowOnError>({
        ...options,
        url: '/admin/milestone-groups/order/'
    });
};

/**
 * Upload Milestone Group Image
 */
export const uploadMilestoneGroupImage = <ThrowOnError extends boolean = false>(options: Options<UploadMilestoneGroupImageData, ThrowOnError>) => {
    return (options?.client ?? client).put<UploadMilestoneGroupImageResponse, UploadMilestoneGroupImageError, ThrowOnError>({
        ...options,
        ...formDataBodySerializer,
        headers: {
            'Content-Type': null,
            ...options?.headers
        },
        url: '/admin/milestone-group-images/{milestone_group_id}'
    });
};

/**
 * Create Milestone
 */
export const createMilestone = <ThrowOnError extends boolean = false>(options: Options<CreateMilestoneData, ThrowOnError>) => {
    return (options?.client ?? client).post<CreateMilestoneResponse, CreateMilestoneError, ThrowOnError>({
        ...options,
        url: '/admin/milestones/{milestone_group_id}'
    });
};

/**
 * Update Milestone
 */
export const updateMilestone = <ThrowOnError extends boolean = false>(options: Options<UpdateMilestoneData, ThrowOnError>) => {
    return (options?.client ?? client).put<UpdateMilestoneResponse, UpdateMilestoneError, ThrowOnError>({
        ...options,
        url: '/admin/milestones/'
    });
};

/**
 * Delete Milestone
 */
export const deleteMilestone = <ThrowOnError extends boolean = false>(options: Options<DeleteMilestoneData, ThrowOnError>) => {
    return (options?.client ?? client).delete<DeleteMilestoneResponse, DeleteMilestoneError, ThrowOnError>({
        ...options,
        url: '/admin/milestones/{milestone_id}'
    });
};

/**
 * Order Milestones Admin
 */
export const orderMilestonesAdmin = <ThrowOnError extends boolean = false>(options: Options<OrderMilestonesAdminData, ThrowOnError>) => {
    return (options?.client ?? client).post<OrderMilestonesAdminResponse, OrderMilestonesAdminError, ThrowOnError>({
        ...options,
        url: '/admin/milestones/order/'
    });
};

/**
 * Upload Milestone Image
 */
export const uploadMilestoneImage = <ThrowOnError extends boolean = false>(options: Options<UploadMilestoneImageData, ThrowOnError>) => {
    return (options?.client ?? client).post<UploadMilestoneImageResponse, UploadMilestoneImageError, ThrowOnError>({
        ...options,
        ...formDataBodySerializer,
        headers: {
            'Content-Type': null,
            ...options?.headers
        },
        url: '/admin/milestone-images/{milestone_id}'
    });
};

/**
 * Delete Milestone Image
 */
export const deleteMilestoneImage = <ThrowOnError extends boolean = false>(options: Options<DeleteMilestoneImageData, ThrowOnError>) => {
    return (options?.client ?? client).delete<DeleteMilestoneImageResponse, DeleteMilestoneImageError, ThrowOnError>({
        ...options,
        url: '/admin/milestone-images/{milestone_image_id}'
    });
};

/**
 * Get Submitted Milestone Images
 */
export const getSubmittedMilestoneImages = <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<GetSubmittedMilestoneImagesResponse, GetSubmittedMilestoneImagesError, ThrowOnError>({
        ...options,
        url: '/admin/submitted-milestone-images/'
    });
};

/**
 * Approve Submitted Milestone Image
 */
export const approveSubmittedMilestoneImage = <ThrowOnError extends boolean = false>(options: Options<ApproveSubmittedMilestoneImageData, ThrowOnError>) => {
    return (options?.client ?? client).post<ApproveSubmittedMilestoneImageResponse, ApproveSubmittedMilestoneImageError, ThrowOnError>({
        ...options,
        url: '/admin/submitted-milestone-images/approve/{submitted_milestone_image_id}'
    });
};

/**
 * Delete Submitted Milestone Image
 */
export const deleteSubmittedMilestoneImage = <ThrowOnError extends boolean = false>(options: Options<DeleteSubmittedMilestoneImageData, ThrowOnError>) => {
    return (options?.client ?? client).delete<DeleteSubmittedMilestoneImageResponse, DeleteSubmittedMilestoneImageError, ThrowOnError>({
        ...options,
        url: '/admin/submitted-milestone-images/{submitted_milestone_image_id}'
    });
};

/**
 * Get Milestone Age Scores
 */
export const getMilestoneAgeScores = <ThrowOnError extends boolean = false>(options: Options<GetMilestoneAgeScoresData, ThrowOnError>) => {
    return (options?.client ?? client).get<GetMilestoneAgeScoresResponse, GetMilestoneAgeScoresError, ThrowOnError>({
        ...options,
        url: '/admin/milestone-age-scores/{milestone_id}'
    });
};

/**
 * Get User Questions Admin
 */
export const getUserQuestionsAdmin = <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<GetUserQuestionsAdminResponse, GetUserQuestionsAdminError, ThrowOnError>({
        ...options,
        url: '/admin/user-questions/'
    });
};

/**
 * Update User Question
 */
export const updateUserQuestion = <ThrowOnError extends boolean = false>(options: Options<UpdateUserQuestionData, ThrowOnError>) => {
    return (options?.client ?? client).put<UpdateUserQuestionResponse, UpdateUserQuestionError, ThrowOnError>({
        ...options,
        url: '/admin/user-questions/'
    });
};

/**
 * Create User Question
 */
export const createUserQuestion = <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => {
    return (options?.client ?? client).post<CreateUserQuestionResponse, CreateUserQuestionError, ThrowOnError>({
        ...options,
        url: '/admin/user-questions/'
    });
};

/**
 * Delete User Question
 */
export const deleteUserQuestion = <ThrowOnError extends boolean = false>(options: Options<DeleteUserQuestionData, ThrowOnError>) => {
    return (options?.client ?? client).delete<DeleteUserQuestionResponse, DeleteUserQuestionError, ThrowOnError>({
        ...options,
        url: '/admin/user-questions/{user_question_id}'
    });
};

/**
 * Order User Questions Admin
 */
export const orderUserQuestionsAdmin = <ThrowOnError extends boolean = false>(options: Options<OrderUserQuestionsAdminData, ThrowOnError>) => {
    return (options?.client ?? client).post<OrderUserQuestionsAdminResponse, OrderUserQuestionsAdminError, ThrowOnError>({
        ...options,
        url: '/admin/user-questions/order/'
    });
};

/**
 * Get Child Questions Admin
 */
export const getChildQuestionsAdmin = <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<GetChildQuestionsAdminResponse, GetChildQuestionsAdminError, ThrowOnError>({
        ...options,
        url: '/admin/child-questions/'
    });
};

/**
 * Update Child Question
 */
export const updateChildQuestion = <ThrowOnError extends boolean = false>(options: Options<UpdateChildQuestionData, ThrowOnError>) => {
    return (options?.client ?? client).put<UpdateChildQuestionResponse, UpdateChildQuestionError, ThrowOnError>({
        ...options,
        url: '/admin/child-questions/'
    });
};

/**
 * Create Child Question
 */
export const createChildQuestion = <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => {
    return (options?.client ?? client).post<CreateChildQuestionResponse, CreateChildQuestionError, ThrowOnError>({
        ...options,
        url: '/admin/child-questions/'
    });
};

/**
 * Delete Child Question
 */
export const deleteChildQuestion = <ThrowOnError extends boolean = false>(options: Options<DeleteChildQuestionData, ThrowOnError>) => {
    return (options?.client ?? client).delete<DeleteChildQuestionResponse, DeleteChildQuestionError, ThrowOnError>({
        ...options,
        url: '/admin/child-questions/{child_question_id}'
    });
};

/**
 * Order Child Questions Admin
 */
export const orderChildQuestionsAdmin = <ThrowOnError extends boolean = false>(options: Options<OrderChildQuestionsAdminData, ThrowOnError>) => {
    return (options?.client ?? client).post<OrderChildQuestionsAdminResponse, OrderChildQuestionsAdminError, ThrowOnError>({
        ...options,
        url: '/admin/child-questions/order/'
    });
};

/**
 * Get Users
 */
export const getUsers = <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<GetUsersResponse, GetUsersError, ThrowOnError>({
        ...options,
        url: '/admin/users/'
    });
};

/**
 * Get Research Groups
 */
export const getResearchGroups = <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<GetResearchGroupsResponse, GetResearchGroupsError, ThrowOnError>({
        ...options,
        url: '/admin/research-groups/'
    });
};

/**
 * Create Research Group
 */
export const createResearchGroup = <ThrowOnError extends boolean = false>(options: Options<CreateResearchGroupData, ThrowOnError>) => {
    return (options?.client ?? client).post<CreateResearchGroupResponse, CreateResearchGroupError, ThrowOnError>({
        ...options,
        url: '/admin/research-groups/{user_id}'
    });
};

/**
 * Delete Research Group
 */
export const deleteResearchGroup = <ThrowOnError extends boolean = false>(options: Options<DeleteResearchGroupData, ThrowOnError>) => {
    return (options?.client ?? client).delete<DeleteResearchGroupResponse, DeleteResearchGroupError, ThrowOnError>({
        ...options,
        url: '/admin/research-groups/{research_group_id}'
    });
};

/**
 * Users:Current User
 */
export const usersCurrentUser = <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<UsersCurrentUserResponse, UsersCurrentUserError, ThrowOnError>({
        ...options,
        url: '/users/me'
    });
};

/**
 * Users:Patch Current User
 */
export const usersPatchCurrentUser = <ThrowOnError extends boolean = false>(options: Options<UsersPatchCurrentUserData, ThrowOnError>) => {
    return (options?.client ?? client).patch<UsersPatchCurrentUserResponse, UsersPatchCurrentUserError, ThrowOnError>({
        ...options,
        url: '/users/me'
    });
};

/**
 * Users:User
 */
export const usersUser = <ThrowOnError extends boolean = false>(options: Options<UsersUserData, ThrowOnError>) => {
    return (options?.client ?? client).get<UsersUserResponse, UsersUserError, ThrowOnError>({
        ...options,
        url: '/users/{id}'
    });
};

/**
 * Users:Patch User
 */
export const usersPatchUser = <ThrowOnError extends boolean = false>(options: Options<UsersPatchUserData, ThrowOnError>) => {
    return (options?.client ?? client).patch<UsersPatchUserResponse, UsersPatchUserError, ThrowOnError>({
        ...options,
        url: '/users/{id}'
    });
};

/**
 * Users:Delete User
 */
export const usersDeleteUser = <ThrowOnError extends boolean = false>(options: Options<UsersDeleteUserData, ThrowOnError>) => {
    return (options?.client ?? client).delete<UsersDeleteUserResponse, UsersDeleteUserError, ThrowOnError>({
        ...options,
        url: '/users/{id}'
    });
};

/**
 * Get Children
 */
export const getChildren = <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<GetChildrenResponse, GetChildrenError, ThrowOnError>({
        ...options,
        url: '/users/children/'
    });
};

/**
 * Update Child
 */
export const updateChild = <ThrowOnError extends boolean = false>(options: Options<UpdateChildData, ThrowOnError>) => {
    return (options?.client ?? client).put<UpdateChildResponse, UpdateChildError, ThrowOnError>({
        ...options,
        url: '/users/children/'
    });
};

/**
 * Create Child
 */
export const createChild = <ThrowOnError extends boolean = false>(options: Options<CreateChildData, ThrowOnError>) => {
    return (options?.client ?? client).post<CreateChildResponse, CreateChildError, ThrowOnError>({
        ...options,
        url: '/users/children/'
    });
};

/**
 * Get Child
 */
export const getChild = <ThrowOnError extends boolean = false>(options: Options<GetChildData, ThrowOnError>) => {
    return (options?.client ?? client).get<GetChildResponse, GetChildError, ThrowOnError>({
        ...options,
        url: '/users/children/{child_id}'
    });
};

/**
 * Delete Child
 */
export const deleteChild = <ThrowOnError extends boolean = false>(options: Options<DeleteChildData, ThrowOnError>) => {
    return (options?.client ?? client).delete<DeleteChildResponse, DeleteChildError, ThrowOnError>({
        ...options,
        url: '/users/children/{child_id}'
    });
};

/**
 * Get Child Image
 */
export const getChildImage = <ThrowOnError extends boolean = false>(options: Options<GetChildImageData, ThrowOnError>) => {
    return (options?.client ?? client).get<GetChildImageResponse, GetChildImageError, ThrowOnError>({
        ...options,
        url: '/users/children-images/{child_id}'
    });
};

/**
 * Upload Child Image
 */
export const uploadChildImage = <ThrowOnError extends boolean = false>(options: Options<UploadChildImageData, ThrowOnError>) => {
    return (options?.client ?? client).put<UploadChildImageResponse, UploadChildImageError, ThrowOnError>({
        ...options,
        ...formDataBodySerializer,
        headers: {
            'Content-Type': null,
            ...options?.headers
        },
        url: '/users/children-images/{child_id}'
    });
};

/**
 * Delete Child Image
 */
export const deleteChildImage = <ThrowOnError extends boolean = false>(options: Options<DeleteChildImageData, ThrowOnError>) => {
    return (options?.client ?? client).delete<DeleteChildImageResponse, DeleteChildImageError, ThrowOnError>({
        ...options,
        url: '/users/children-images/{child_id}'
    });
};

/**
 * Get Current Milestone Answer Session
 */
export const getCurrentMilestoneAnswerSession = <ThrowOnError extends boolean = false>(options: Options<GetCurrentMilestoneAnswerSessionData, ThrowOnError>) => {
    return (options?.client ?? client).get<GetCurrentMilestoneAnswerSessionResponse, GetCurrentMilestoneAnswerSessionError, ThrowOnError>({
        ...options,
        url: '/users/milestone-answers/{child_id}'
    });
};

/**
 * Update Milestone Answer
 */
export const updateMilestoneAnswer = <ThrowOnError extends boolean = false>(options: Options<UpdateMilestoneAnswerData, ThrowOnError>) => {
    return (options?.client ?? client).put<UpdateMilestoneAnswerResponse, UpdateMilestoneAnswerError, ThrowOnError>({
        ...options,
        url: '/users/milestone-answers/{milestone_answer_session_id}'
    });
};

/**
 * Get Current User Answers
 */
export const getCurrentUserAnswers = <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<GetCurrentUserAnswersResponse, GetCurrentUserAnswersError, ThrowOnError>({
        ...options,
        url: '/users/user-answers/'
    });
};

/**
 * Update Current User Answers
 */
export const updateCurrentUserAnswers = <ThrowOnError extends boolean = false>(options: Options<UpdateCurrentUserAnswersData, ThrowOnError>) => {
    return (options?.client ?? client).put<UpdateCurrentUserAnswersResponse, UpdateCurrentUserAnswersError, ThrowOnError>({
        ...options,
        url: '/users/user-answers/'
    });
};

/**
 * Get Current Child Answers
 */
export const getCurrentChildAnswers = <ThrowOnError extends boolean = false>(options: Options<GetCurrentChildAnswersData, ThrowOnError>) => {
    return (options?.client ?? client).get<GetCurrentChildAnswersResponse, GetCurrentChildAnswersError, ThrowOnError>({
        ...options,
        url: '/users/children-answers/{child_id}'
    });
};

/**
 * Update Current Child Answers
 */
export const updateCurrentChildAnswers = <ThrowOnError extends boolean = false>(options: Options<UpdateCurrentChildAnswersData, ThrowOnError>) => {
    return (options?.client ?? client).put<UpdateCurrentChildAnswersResponse, UpdateCurrentChildAnswersError, ThrowOnError>({
        ...options,
        url: '/users/children-answers/{child_id}'
    });
};

/**
 * Get Milestone Answer Sessions In Statistics
 */
export const getMilestoneAnswerSessionsInStatistics = <ThrowOnError extends boolean = false>(options: Options<GetMilestoneAnswerSessionsInStatisticsData, ThrowOnError>) => {
    return (options?.client ?? client).get<GetMilestoneAnswerSessionsInStatisticsResponse, GetMilestoneAnswerSessionsInStatisticsError, ThrowOnError>({
        ...options,
        url: '/users/milestone-answers-sessions/{child_id}'
    });
};

/**
 * Get Milestonegroups For Session
 */
export const getMilestonegroupsForSession = <ThrowOnError extends boolean = false>(options: Options<GetMilestonegroupsForSessionData, ThrowOnError>) => {
    return (options?.client ?? client).get<GetMilestonegroupsForSessionResponse, GetMilestonegroupsForSessionError, ThrowOnError>({
        ...options,
        url: '/users/feedback/answersession={answersession_id}'
    });
};

/**
 * Get Summary Feedback For Answersession
 */
export const getSummaryFeedbackForAnswersession = <ThrowOnError extends boolean = false>(options: Options<GetSummaryFeedbackForAnswersessionData, ThrowOnError>) => {
    return (options?.client ?? client).get<GetSummaryFeedbackForAnswersessionResponse, GetSummaryFeedbackForAnswersessionError, ThrowOnError>({
        ...options,
        url: '/users/feedback/answersession={answersession_id}/summary'
    });
};

/**
 * Get Detailed Feedback For Answersession
 */
export const getDetailedFeedbackForAnswersession = <ThrowOnError extends boolean = false>(options: Options<GetDetailedFeedbackForAnswersessionData, ThrowOnError>) => {
    return (options?.client ?? client).get<GetDetailedFeedbackForAnswersessionResponse, GetDetailedFeedbackForAnswersessionError, ThrowOnError>({
        ...options,
        url: '/users/feedback/answersession={answersession_id}/detailed'
    });
};

/**
 * Auth:Cookie.Login
 */
export const authCookieLogin = <ThrowOnError extends boolean = false>(options: Options<AuthCookieLoginData, ThrowOnError>) => {
    return (options?.client ?? client).post<AuthCookieLoginResponse, AuthCookieLoginError, ThrowOnError>({
        ...options,
        ...urlSearchParamsBodySerializer,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            ...options?.headers
        },
        url: '/auth/login'
    });
};

/**
 * Auth:Cookie.Logout
 */
export const authCookieLogout = <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => {
    return (options?.client ?? client).post<AuthCookieLogoutResponse, AuthCookieLogoutError, ThrowOnError>({
        ...options,
        url: '/auth/logout'
    });
};

/**
 * Register:Register
 */
export const registerRegister = <ThrowOnError extends boolean = false>(options: Options<RegisterRegisterData, ThrowOnError>) => {
    return (options?.client ?? client).post<RegisterRegisterResponse, RegisterRegisterError, ThrowOnError>({
        ...options,
        url: '/auth/register'
    });
};

/**
 * Reset:Forgot Password
 */
export const resetForgotPassword = <ThrowOnError extends boolean = false>(options: Options<ResetForgotPasswordData, ThrowOnError>) => {
    return (options?.client ?? client).post<ResetForgotPasswordResponse, ResetForgotPasswordError, ThrowOnError>({
        ...options,
        url: '/auth/forgot-password'
    });
};

/**
 * Reset:Reset Password
 */
export const resetResetPassword = <ThrowOnError extends boolean = false>(options: Options<ResetResetPasswordData, ThrowOnError>) => {
    return (options?.client ?? client).post<ResetResetPasswordResponse, ResetResetPasswordError, ThrowOnError>({
        ...options,
        url: '/auth/reset-password'
    });
};

/**
 * Verify:Request-Token
 */
export const verifyRequestToken = <ThrowOnError extends boolean = false>(options: Options<VerifyRequestTokenData, ThrowOnError>) => {
    return (options?.client ?? client).post<VerifyRequestTokenResponse, VerifyRequestTokenError, ThrowOnError>({
        ...options,
        url: '/auth/request-verify-token'
    });
};

/**
 * Verify:Verify
 */
export const verifyVerify = <ThrowOnError extends boolean = false>(options: Options<VerifyVerifyData, ThrowOnError>) => {
    return (options?.client ?? client).post<VerifyVerifyResponse, VerifyVerifyError, ThrowOnError>({
        ...options,
        url: '/auth/verify'
    });
};

/**
 * Auth
 */
export const auth = <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<AuthResponse, AuthError, ThrowOnError>({
        ...options,
        url: '/research/auth/'
    });
};