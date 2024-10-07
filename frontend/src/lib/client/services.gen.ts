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
	GetMilestoneGroupsError,
	GetMilestoneGroupsResponse,
	GetMilestoneGroupData,
	GetMilestoneGroupError,
	GetMilestoneGroupResponse,
	GetUserQuestionsError,
	GetUserQuestionsResponse,
	CreateLanguageData,
	CreateLanguageError,
	CreateLanguageResponse,
	DeleteLanguageData,
	DeleteLanguageError,
	DeleteLanguageResponse,
	GetMilestoneGroupsAdminError,
	GetMilestoneGroupsAdminResponse,
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
	GetUserQuestions1Error,
	GetUserQuestions1Response,
	UpdateUserQuestionData,
	UpdateUserQuestionError,
	UpdateUserQuestionResponse,
	CreateUserQuestionError,
	CreateUserQuestionResponse,
	DeleteQuestionData,
	DeleteQuestionError,
	DeleteQuestionResponse,
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
	options?: Options<unknown, ThrowOnError>
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
 * Get Milestone Groups Admin
 */
export const getMilestoneGroupsAdmin = <ThrowOnError extends boolean = false>(
	options?: Options<unknown, ThrowOnError>
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
	options?: Options<unknown, ThrowOnError>
) => {
	return (options?.client ?? client).post<
		CreateMilestoneGroupAdminResponse,
		CreateMilestoneGroupAdminError,
		ThrowOnError
	>({
		...options,
		url: '/admin/milestone-groups/'
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
 * Get User Questions
 */
export const getUserQuestions1 = <ThrowOnError extends boolean = false>(
	options?: Options<unknown, ThrowOnError>
) => {
	return (options?.client ?? client).get<
		GetUserQuestions1Response,
		GetUserQuestions1Error,
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
 * Delete Question
 */
export const deleteQuestion = <ThrowOnError extends boolean = false>(
	options: Options<DeleteQuestionData, ThrowOnError>
) => {
	return (options?.client ?? client).delete<
		DeleteQuestionResponse,
		DeleteQuestionError,
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
