// This file is auto-generated by @hey-api/openapi-ts

import {
	createClient,
	createConfig,
	type Options,
	formDataBodySerializer,
	urlSearchParamsBodySerializer
} from '@hey-api/client-fetch';
import type {
	GetLanguagesError,
	GetLanguagesResponse,
	GetMilestonesError,
	GetMilestonesResponse,
	GetMilestoneData,
	GetMilestoneError,
	GetMilestoneResponse,
	GetMilestoneGroupsData,
	GetMilestoneGroupsError,
	GetMilestoneGroupsResponse,
	GetMilestoneGroupData,
	GetMilestoneGroupError,
	GetMilestoneGroupResponse,
	GetMilestoneAgeGroupsError,
	GetMilestoneAgeGroupsResponse,
	GetUserQuestionsError,
	GetUserQuestionsResponse,
	CreateLanguageData,
	CreateLanguageError,
	CreateLanguageResponse,
	DeleteLanguageData,
	DeleteLanguageError,
	DeleteLanguageResponse,
	UpdateI18NData,
	UpdateI18NError,
	UpdateI18NResponse,
	UpdateMilestoneAgeGroupData,
	UpdateMilestoneAgeGroupError,
	UpdateMilestoneAgeGroupResponse,
	CreateMilestoneAgeGroupData,
	CreateMilestoneAgeGroupError,
	CreateMilestoneAgeGroupResponse,
	DeleteMilestoneAgeGroupData,
	DeleteMilestoneAgeGroupError,
	DeleteMilestoneAgeGroupResponse,
	GetMilestoneGroupsAdminData,
	GetMilestoneGroupsAdminError,
	GetMilestoneGroupsAdminResponse,
	CreateMilestoneGroupAdminData,
	CreateMilestoneGroupAdminError,
	CreateMilestoneGroupAdminResponse,
	UpdateMilestoneGroupAdminData,
	UpdateMilestoneGroupAdminError,
	UpdateMilestoneGroupAdminResponse,
	DeleteMilestoneGroupAdminData,
	DeleteMilestoneGroupAdminError,
	DeleteMilestoneGroupAdminResponse,
	UploadMilestoneGroupImageData,
	UploadMilestoneGroupImageError,
	UploadMilestoneGroupImageResponse,
	CreateMilestoneData,
	CreateMilestoneError,
	CreateMilestoneResponse,
	UpdateMilestoneData,
	UpdateMilestoneError,
	UpdateMilestoneResponse,
	DeleteMilestoneData,
	DeleteMilestoneError,
	DeleteMilestoneResponse,
	UploadMilestoneImageData,
	UploadMilestoneImageError,
	UploadMilestoneImageResponse,
	GetUserQuestionsAdminError,
	GetUserQuestionsAdminResponse,
	UpdateUserQuestionData,
	UpdateUserQuestionError,
	UpdateUserQuestionResponse,
	CreateUserQuestionError,
	CreateUserQuestionResponse,
	DeleteUserQuestionData,
	DeleteUserQuestionError,
	DeleteUserQuestionResponse,
	UsersCurrentUserError,
	UsersCurrentUserResponse,
	UsersPatchCurrentUserData,
	UsersPatchCurrentUserError,
	UsersPatchCurrentUserResponse,
	UsersUserData,
	UsersUserError,
	UsersUserResponse,
	UsersPatchUserData,
	UsersPatchUserError,
	UsersPatchUserResponse,
	UsersDeleteUserData,
	UsersDeleteUserError,
	UsersDeleteUserResponse,
	GetChildrenError,
	GetChildrenResponse,
	UpdateChildData,
	UpdateChildError,
	UpdateChildResponse,
	CreateChildData,
	CreateChildError,
	CreateChildResponse,
	DeleteChildData,
	DeleteChildError,
	DeleteChildResponse,
	GetChildImageData,
	GetChildImageError,
	GetChildImageResponse,
	UploadChildImageData,
	UploadChildImageError,
	UploadChildImageResponse,
	GetCurrentMilestoneAnswerSessionData,
	GetCurrentMilestoneAnswerSessionError,
	GetCurrentMilestoneAnswerSessionResponse,
	UpdateMilestoneAnswerData,
	UpdateMilestoneAnswerError,
	UpdateMilestoneAnswerResponse,
	GetCurrentUserAnswersError,
	GetCurrentUserAnswersResponse,
	UpdateCurrentUserAnswersData,
	UpdateCurrentUserAnswersError,
	UpdateCurrentUserAnswersResponse,
	AuthCookieLoginData,
	AuthCookieLoginError,
	AuthCookieLoginResponse,
	AuthCookieLogoutError,
	AuthCookieLogoutResponse,
	RegisterRegisterData,
	RegisterRegisterError,
	RegisterRegisterResponse,
	ResetForgotPasswordData,
	ResetForgotPasswordError,
	ResetForgotPasswordResponse,
	ResetResetPasswordData,
	ResetResetPasswordError,
	ResetResetPasswordResponse,
	VerifyRequestTokenData,
	VerifyRequestTokenError,
	VerifyRequestTokenResponse,
	VerifyVerifyData,
	VerifyVerifyError,
	VerifyVerifyResponse,
	AuthError,
	AuthResponse
} from './types.gen';

export const client = createClient(createConfig());

/**
 * Get Languages
 */
export const getLanguages = <ThrowOnError extends boolean = false>(
	options?: Options<unknown, ThrowOnError>
) => {
	return (options?.client ?? client).get<GetLanguagesResponse, GetLanguagesError, ThrowOnError>({
		...options,
		url: '/languages/'
	});
};

/**
 * Get Milestones
 */
export const getMilestones = <ThrowOnError extends boolean = false>(
	options?: Options<unknown, ThrowOnError>
) => {
	return (options?.client ?? client).get<GetMilestonesResponse, GetMilestonesError, ThrowOnError>({
		...options,
		url: '/milestones/'
	});
};

/**
 * Get Milestone
 */
export const getMilestone = <ThrowOnError extends boolean = false>(
	options: Options<GetMilestoneData, ThrowOnError>
) => {
	return (options?.client ?? client).get<GetMilestoneResponse, GetMilestoneError, ThrowOnError>({
		...options,
		url: '/milestones/{milestone_id}'
	});
};

/**
 * Get Milestone Groups
 */
export const getMilestoneGroups = <ThrowOnError extends boolean = false>(
	options: Options<GetMilestoneGroupsData, ThrowOnError>
) => {
	return (options?.client ?? client).get<
		GetMilestoneGroupsResponse,
		GetMilestoneGroupsError,
		ThrowOnError
	>({
		...options,
		url: '/milestone-groups/'
	});
};

/**
 * Get Milestone Group
 */
export const getMilestoneGroup = <ThrowOnError extends boolean = false>(
	options: Options<GetMilestoneGroupData, ThrowOnError>
) => {
	return (options?.client ?? client).get<
		GetMilestoneGroupResponse,
		GetMilestoneGroupError,
		ThrowOnError
	>({
		...options,
		url: '/milestone-groups/{milestone_group_id}'
	});
};

/**
 * Get Milestone Age Groups
 */
export const getMilestoneAgeGroups = <ThrowOnError extends boolean = false>(
	options?: Options<unknown, ThrowOnError>
) => {
	return (options?.client ?? client).get<
		GetMilestoneAgeGroupsResponse,
		GetMilestoneAgeGroupsError,
		ThrowOnError
	>({
		...options,
		url: '/milestone-age-groups/'
	});
};

/**
 * Get User Questions
 */
export const getUserQuestions = <ThrowOnError extends boolean = false>(
	options?: Options<unknown, ThrowOnError>
) => {
	return (options?.client ?? client).get<
		GetUserQuestionsResponse,
		GetUserQuestionsError,
		ThrowOnError
	>({
		...options,
		url: '/user-questions/'
	});
};

/**
 * Create Language
 */
export const createLanguage = <ThrowOnError extends boolean = false>(
	options: Options<CreateLanguageData, ThrowOnError>
) => {
	return (options?.client ?? client).post<
		CreateLanguageResponse,
		CreateLanguageError,
		ThrowOnError
	>({
		...options,
		url: '/admin/languages/'
	});
};

/**
 * Delete Language
 */
export const deleteLanguage = <ThrowOnError extends boolean = false>(
	options: Options<DeleteLanguageData, ThrowOnError>
) => {
	return (options?.client ?? client).delete<
		DeleteLanguageResponse,
		DeleteLanguageError,
		ThrowOnError
	>({
		...options,
		url: '/admin/languages/{language_id}'
	});
};

/**
 * Update I18N
 */
export const updateI18N = <ThrowOnError extends boolean = false>(
	options: Options<UpdateI18NData, ThrowOnError>
) => {
	return (options?.client ?? client).put<UpdateI18NResponse, UpdateI18NError, ThrowOnError>({
		...options,
		url: '/admin/i18n/{language_id}'
	});
};

/**
 * Update Milestone Age Group
 */
export const updateMilestoneAgeGroup = <ThrowOnError extends boolean = false>(
	options: Options<UpdateMilestoneAgeGroupData, ThrowOnError>
) => {
	return (options?.client ?? client).put<
		UpdateMilestoneAgeGroupResponse,
		UpdateMilestoneAgeGroupError,
		ThrowOnError
	>({
		...options,
		url: '/admin/milestone-age-groups/'
	});
};

/**
 * Create Milestone Age Group
 */
export const createMilestoneAgeGroup = <ThrowOnError extends boolean = false>(
	options: Options<CreateMilestoneAgeGroupData, ThrowOnError>
) => {
	return (options?.client ?? client).post<
		CreateMilestoneAgeGroupResponse,
		CreateMilestoneAgeGroupError,
		ThrowOnError
	>({
		...options,
		url: '/admin/milestone-age-groups/'
	});
};

/**
 * Delete Milestone Age Group
 */
export const deleteMilestoneAgeGroup = <ThrowOnError extends boolean = false>(
	options: Options<DeleteMilestoneAgeGroupData, ThrowOnError>
) => {
	return (options?.client ?? client).delete<
		DeleteMilestoneAgeGroupResponse,
		DeleteMilestoneAgeGroupError,
		ThrowOnError
	>({
		...options,
		url: '/admin/milestone-age-groups/{milestone_age_group_id}'
	});
};

/**
 * Get Milestone Groups Admin
 */
export const getMilestoneGroupsAdmin = <ThrowOnError extends boolean = false>(
	options: Options<GetMilestoneGroupsAdminData, ThrowOnError>
) => {
	return (options?.client ?? client).get<
		GetMilestoneGroupsAdminResponse,
		GetMilestoneGroupsAdminError,
		ThrowOnError
	>({
		...options,
		url: '/admin/milestone-groups/'
	});
};

/**
 * Create Milestone Group Admin
 */
export const createMilestoneGroupAdmin = <ThrowOnError extends boolean = false>(
	options: Options<CreateMilestoneGroupAdminData, ThrowOnError>
) => {
	return (options?.client ?? client).post<
		CreateMilestoneGroupAdminResponse,
		CreateMilestoneGroupAdminError,
		ThrowOnError
	>({
		...options,
		url: '/admin/milestone-groups/{milestone_age_group_id}'
	});
};

/**
 * Update Milestone Group Admin
 */
export const updateMilestoneGroupAdmin = <ThrowOnError extends boolean = false>(
	options: Options<UpdateMilestoneGroupAdminData, ThrowOnError>
) => {
	return (options?.client ?? client).put<
		UpdateMilestoneGroupAdminResponse,
		UpdateMilestoneGroupAdminError,
		ThrowOnError
	>({
		...options,
		url: '/admin/milestone-groups'
	});
};

/**
 * Delete Milestone Group Admin
 */
export const deleteMilestoneGroupAdmin = <ThrowOnError extends boolean = false>(
	options: Options<DeleteMilestoneGroupAdminData, ThrowOnError>
) => {
	return (options?.client ?? client).delete<
		DeleteMilestoneGroupAdminResponse,
		DeleteMilestoneGroupAdminError,
		ThrowOnError
	>({
		...options,
		url: '/admin/milestone-groups/{milestone_group_id}'
	});
};

/**
 * Upload Milestone Group Image
 */
export const uploadMilestoneGroupImage = <ThrowOnError extends boolean = false>(
	options: Options<UploadMilestoneGroupImageData, ThrowOnError>
) => {
	return (options?.client ?? client).put<
		UploadMilestoneGroupImageResponse,
		UploadMilestoneGroupImageError,
		ThrowOnError
	>({
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
export const createMilestone = <ThrowOnError extends boolean = false>(
	options: Options<CreateMilestoneData, ThrowOnError>
) => {
	return (options?.client ?? client).post<
		CreateMilestoneResponse,
		CreateMilestoneError,
		ThrowOnError
	>({
		...options,
		url: '/admin/milestones/{milestone_group_id}'
	});
};

/**
 * Update Milestone
 */
export const updateMilestone = <ThrowOnError extends boolean = false>(
	options: Options<UpdateMilestoneData, ThrowOnError>
) => {
	return (options?.client ?? client).put<
		UpdateMilestoneResponse,
		UpdateMilestoneError,
		ThrowOnError
	>({
		...options,
		url: '/admin/milestones/'
	});
};

/**
 * Delete Milestone
 */
export const deleteMilestone = <ThrowOnError extends boolean = false>(
	options: Options<DeleteMilestoneData, ThrowOnError>
) => {
	return (options?.client ?? client).delete<
		DeleteMilestoneResponse,
		DeleteMilestoneError,
		ThrowOnError
	>({
		...options,
		url: '/admin/milestones/{milestone_id}'
	});
};

/**
 * Upload Milestone Image
 */
export const uploadMilestoneImage = <ThrowOnError extends boolean = false>(
	options: Options<UploadMilestoneImageData, ThrowOnError>
) => {
	return (options?.client ?? client).post<
		UploadMilestoneImageResponse,
		UploadMilestoneImageError,
		ThrowOnError
	>({
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
 * Get User Questions Admin
 */
export const getUserQuestionsAdmin = <ThrowOnError extends boolean = false>(
	options?: Options<unknown, ThrowOnError>
) => {
	return (options?.client ?? client).get<
		GetUserQuestionsAdminResponse,
		GetUserQuestionsAdminError,
		ThrowOnError
	>({
		...options,
		url: '/admin/user-questions/'
	});
};

/**
 * Update User Question
 */
export const updateUserQuestion = <ThrowOnError extends boolean = false>(
	options: Options<UpdateUserQuestionData, ThrowOnError>
) => {
	return (options?.client ?? client).put<
		UpdateUserQuestionResponse,
		UpdateUserQuestionError,
		ThrowOnError
	>({
		...options,
		url: '/admin/user-questions/'
	});
};

/**
 * Create User Question
 */
export const createUserQuestion = <ThrowOnError extends boolean = false>(
	options?: Options<unknown, ThrowOnError>
) => {
	return (options?.client ?? client).post<
		CreateUserQuestionResponse,
		CreateUserQuestionError,
		ThrowOnError
	>({
		...options,
		url: '/admin/user-questions/'
	});
};

/**
 * Delete User Question
 */
export const deleteUserQuestion = <ThrowOnError extends boolean = false>(
	options: Options<DeleteUserQuestionData, ThrowOnError>
) => {
	return (options?.client ?? client).delete<
		DeleteUserQuestionResponse,
		DeleteUserQuestionError,
		ThrowOnError
	>({
		...options,
		url: '/admin/user-questions/{user_question_id}'
	});
};

/**
 * Users:Current User
 */
export const usersCurrentUser = <ThrowOnError extends boolean = false>(
	options?: Options<unknown, ThrowOnError>
) => {
	return (options?.client ?? client).get<
		UsersCurrentUserResponse,
		UsersCurrentUserError,
		ThrowOnError
	>({
		...options,
		url: '/users/me'
	});
};

/**
 * Users:Patch Current User
 */
export const usersPatchCurrentUser = <ThrowOnError extends boolean = false>(
	options: Options<UsersPatchCurrentUserData, ThrowOnError>
) => {
	return (options?.client ?? client).patch<
		UsersPatchCurrentUserResponse,
		UsersPatchCurrentUserError,
		ThrowOnError
	>({
		...options,
		url: '/users/me'
	});
};

/**
 * Users:User
 */
export const usersUser = <ThrowOnError extends boolean = false>(
	options: Options<UsersUserData, ThrowOnError>
) => {
	return (options?.client ?? client).get<UsersUserResponse, UsersUserError, ThrowOnError>({
		...options,
		url: '/users/{id}'
	});
};

/**
 * Users:Patch User
 */
export const usersPatchUser = <ThrowOnError extends boolean = false>(
	options: Options<UsersPatchUserData, ThrowOnError>
) => {
	return (options?.client ?? client).patch<
		UsersPatchUserResponse,
		UsersPatchUserError,
		ThrowOnError
	>({
		...options,
		url: '/users/{id}'
	});
};

/**
 * Users:Delete User
 */
export const usersDeleteUser = <ThrowOnError extends boolean = false>(
	options: Options<UsersDeleteUserData, ThrowOnError>
) => {
	return (options?.client ?? client).delete<
		UsersDeleteUserResponse,
		UsersDeleteUserError,
		ThrowOnError
	>({
		...options,
		url: '/users/{id}'
	});
};

/**
 * Get Children
 */
export const getChildren = <ThrowOnError extends boolean = false>(
	options?: Options<unknown, ThrowOnError>
) => {
	return (options?.client ?? client).get<GetChildrenResponse, GetChildrenError, ThrowOnError>({
		...options,
		url: '/users/children/'
	});
};

/**
 * Update Child
 */
export const updateChild = <ThrowOnError extends boolean = false>(
	options: Options<UpdateChildData, ThrowOnError>
) => {
	return (options?.client ?? client).put<UpdateChildResponse, UpdateChildError, ThrowOnError>({
		...options,
		url: '/users/children/'
	});
};

/**
 * Create Child
 */
export const createChild = <ThrowOnError extends boolean = false>(
	options: Options<CreateChildData, ThrowOnError>
) => {
	return (options?.client ?? client).post<CreateChildResponse, CreateChildError, ThrowOnError>({
		...options,
		url: '/users/children/'
	});
};

/**
 * Delete Child
 */
export const deleteChild = <ThrowOnError extends boolean = false>(
	options: Options<DeleteChildData, ThrowOnError>
) => {
	return (options?.client ?? client).delete<DeleteChildResponse, DeleteChildError, ThrowOnError>({
		...options,
		url: '/users/children/{child_id}'
	});
};

/**
 * Get Child Image
 */
export const getChildImage = <ThrowOnError extends boolean = false>(
	options: Options<GetChildImageData, ThrowOnError>
) => {
	return (options?.client ?? client).get<GetChildImageResponse, GetChildImageError, ThrowOnError>({
		...options,
		url: '/users/children-images/{child_id}'
	});
};

/**
 * Upload Child Image
 */
export const uploadChildImage = <ThrowOnError extends boolean = false>(
	options: Options<UploadChildImageData, ThrowOnError>
) => {
	return (options?.client ?? client).put<
		UploadChildImageResponse,
		UploadChildImageError,
		ThrowOnError
	>({
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
 * Get Current Milestone Answer Session
 */
export const getCurrentMilestoneAnswerSession = <ThrowOnError extends boolean = false>(
	options: Options<GetCurrentMilestoneAnswerSessionData, ThrowOnError>
) => {
	return (options?.client ?? client).get<
		GetCurrentMilestoneAnswerSessionResponse,
		GetCurrentMilestoneAnswerSessionError,
		ThrowOnError
	>({
		...options,
		url: '/users/milestone-answers/{child_id}'
	});
};

/**
 * Update Milestone Answer
 */
export const updateMilestoneAnswer = <ThrowOnError extends boolean = false>(
	options: Options<UpdateMilestoneAnswerData, ThrowOnError>
) => {
	return (options?.client ?? client).put<
		UpdateMilestoneAnswerResponse,
		UpdateMilestoneAnswerError,
		ThrowOnError
	>({
		...options,
		url: '/users/milestone-answers/{milestone_answer_session_id}'
	});
};

/**
 * Get Current User Answers
 */
export const getCurrentUserAnswers = <ThrowOnError extends boolean = false>(
	options?: Options<unknown, ThrowOnError>
) => {
	return (options?.client ?? client).get<
		GetCurrentUserAnswersResponse,
		GetCurrentUserAnswersError,
		ThrowOnError
	>({
		...options,
		url: '/users/user-answers/'
	});
};

/**
 * Update Current User Answers
 */
export const updateCurrentUserAnswers = <ThrowOnError extends boolean = false>(
	options: Options<UpdateCurrentUserAnswersData, ThrowOnError>
) => {
	return (options?.client ?? client).put<
		UpdateCurrentUserAnswersResponse,
		UpdateCurrentUserAnswersError,
		ThrowOnError
	>({
		...options,
		url: '/users/user-answers/'
	});
};

/**
 * Auth:Cookie.Login
 */
export const authCookieLogin = <ThrowOnError extends boolean = false>(
	options: Options<AuthCookieLoginData, ThrowOnError>
) => {
	return (options?.client ?? client).post<
		AuthCookieLoginResponse,
		AuthCookieLoginError,
		ThrowOnError
	>({
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
export const authCookieLogout = <ThrowOnError extends boolean = false>(
	options?: Options<unknown, ThrowOnError>
) => {
	return (options?.client ?? client).post<
		AuthCookieLogoutResponse,
		AuthCookieLogoutError,
		ThrowOnError
	>({
		...options,
		url: '/auth/logout'
	});
};

/**
 * Register:Register
 */
export const registerRegister = <ThrowOnError extends boolean = false>(
	options: Options<RegisterRegisterData, ThrowOnError>
) => {
	return (options?.client ?? client).post<
		RegisterRegisterResponse,
		RegisterRegisterError,
		ThrowOnError
	>({
		...options,
		url: '/auth/register'
	});
};

/**
 * Reset:Forgot Password
 */
export const resetForgotPassword = <ThrowOnError extends boolean = false>(
	options: Options<ResetForgotPasswordData, ThrowOnError>
) => {
	return (options?.client ?? client).post<
		ResetForgotPasswordResponse,
		ResetForgotPasswordError,
		ThrowOnError
	>({
		...options,
		url: '/auth/forgot-password'
	});
};

/**
 * Reset:Reset Password
 */
export const resetResetPassword = <ThrowOnError extends boolean = false>(
	options: Options<ResetResetPasswordData, ThrowOnError>
) => {
	return (options?.client ?? client).post<
		ResetResetPasswordResponse,
		ResetResetPasswordError,
		ThrowOnError
	>({
		...options,
		url: '/auth/reset-password'
	});
};

/**
 * Verify:Request-Token
 */
export const verifyRequestToken = <ThrowOnError extends boolean = false>(
	options: Options<VerifyRequestTokenData, ThrowOnError>
) => {
	return (options?.client ?? client).post<
		VerifyRequestTokenResponse,
		VerifyRequestTokenError,
		ThrowOnError
	>({
		...options,
		url: '/auth/request-verify-token'
	});
};

/**
 * Verify:Verify
 */
export const verifyVerify = <ThrowOnError extends boolean = false>(
	options: Options<VerifyVerifyData, ThrowOnError>
) => {
	return (options?.client ?? client).post<VerifyVerifyResponse, VerifyVerifyError, ThrowOnError>({
		...options,
		url: '/auth/verify'
	});
};

/**
 * Auth
 */
export const auth = <ThrowOnError extends boolean = false>(
	options?: Options<unknown, ThrowOnError>
) => {
	return (options?.client ?? client).get<AuthResponse, AuthError, ThrowOnError>({
		...options,
		url: '/research/auth/'
	});
};
