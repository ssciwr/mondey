// This file is auto-generated by @hey-api/openapi-ts

export type Body_auth_cookie_login_auth_login_post = {
    grant_type?: (string | null);
    username: string;
    password: string;
    scope?: string;
    client_id?: (string | null);
    client_secret?: (string | null);
};

export type Body_reset_forgot_password_auth_forgot_password_post = {
    email: string;
};

export type Body_reset_reset_password_auth_reset_password_post = {
    token: string;
    password: string;
};

export type Body_upload_child_image_users_children_images__child_id__put = {
    file: (Blob | File);
};

export type Body_upload_milestone_group_image_admin_milestone_group_images__milestone_group_id__put = {
    file: (Blob | File);
};

export type Body_upload_milestone_image_admin_milestone_images__milestone_id__post = {
    file: (Blob | File);
};

export type Body_verify_request_token_auth_request_verify_token_post = {
    email: string;
};

export type Body_verify_verify_auth_verify_post = {
    token: string;
};

/**
 * External data model for UserAnswers
 *
 * Parameters
 * ----------
 * SQLModel : Pydantic model  basic sqlmodel pydantic type
 */
export type ChildAnswerPublic = {
	answer: string;
	question_id: number;
	additional_answer: string | null;
};

export type ChildCreate = {
    name?: string;
    birth_year: number;
    birth_month: number;
};

export type ChildPublic = {
    name?: string;
    birth_year: number;
    birth_month: number;
    id: number;
    has_image: boolean;
};

export type ChildQuestionAdmin = {
	id: number;
	order: number;
	component?: string;
	type?: string;
	options: string;
	text?: {
		[key: string]: ChildQuestionText;
	};
	additional_option?: string;
};

export type ChildQuestionPublic = {
	id: number;
	component?: string;
	type?: string;
	text?: {
		[key: string]: ChildQuestionTextPublic;
	};
	additional_option?: string;
};

export type ChildQuestionText = {
	question?: string;
	options_json?: string;
	child_question_id?: number | null;
	lang_id?: string | null;
	options?: string;
};

export type ChildQuestionTextPublic = {
	question?: string;
	options_json?: string;
};

export type ErrorModel = {
    detail: (string | {
    [key: string]: (string);
});
};

export type HTTPValidationError = {
    detail?: Array<ValidationError>;
};

export type Language = {
    id: string;
};

export type MilestoneAdmin = {
    id: number;
    group_id: number;
    order: number;
    text?: {
        [key: string]: MilestoneText;
    };
    images?: Array<MilestoneImage>;
};

export type MilestoneAnswerPublic = {
    milestone_id: number;
    answer: number;
};

export type MilestoneAnswerSessionPublic = {
    id: number;
    child_id: number;
    created_at: string;
    answers: {
        [key: string]: MilestoneAnswerPublic;
    };
};

export type MilestoneGroupAdmin = {
    id: number;
    order: number;
    text?: {
        [key: string]: MilestoneGroupText;
    };
    milestones?: Array<MilestoneAdmin>;
};

export type MilestoneGroupPublic = {
    id: number;
    text?: {
        [key: string]: MilestoneGroupTextPublic;
    };
    milestones?: Array<MilestonePublic>;
};

export type MilestoneGroupText = {
    title?: string;
    desc?: string;
    group_id?: (number | null);
    lang_id?: (string | null);
};

export type MilestoneGroupTextPublic = {
    title?: string;
    desc?: string;
};

export type MilestoneImage = {
    id?: (number | null);
    milestone_id?: (number | null);
    filename?: string;
    approved?: boolean;
};

export type MilestoneImagePublic = {
    filename: string;
    approved: boolean;
};

export type MilestonePublic = {
    id: number;
    text?: {
        [key: string]: MilestoneTextPublic;
    };
    images?: Array<MilestoneImagePublic>;
};

export type MilestoneText = {
    title?: string;
    desc?: string;
    obs?: string;
    help?: string;
    milestone_id?: (number | null);
    lang_id?: (string | null);
};

export type MilestoneTextPublic = {
    title?: string;
    desc?: string;
    obs?: string;
    help?: string;
};

/**
 * External data model for UserAnswers
 *
 * Parameters
 * ----------
 * SQLModel : Pydantic model  basic sqlmodel pydantic type
 */
export type UserAnswerPublic = {
    answer: string;
    question_id: number;
    additional_answer: (string | null);
};

export type UserCreate = {
    email: string;
    password: string;
    is_active?: (boolean | null);
    is_superuser?: (boolean | null);
    is_verified?: (boolean | null);
    is_researcher?: (boolean | null);
};

export type UserQuestionAdmin = {
    id: number;
    order: number;
    component?: string;
    type?: string;
    options: string;
    text?: {
        [key: string]: UserQuestionText;
    };
    additional_option?: string;
};

export type UserQuestionPublic = {
    id: number;
    component?: string;
    type?: string;
    text?: {
        [key: string]: UserQuestionTextPublic;
    };
    additional_option?: string;
};

export type UserQuestionText = {
    question?: string;
    options_json?: string;
    user_question_id?: (number | null);
    lang_id?: (string | null);
    options?: string;
};

export type UserQuestionTextPublic = {
    question?: string;
    options_json?: string;
};

export type UserRead = {
    id: number;
    email: string;
    is_active?: boolean;
    is_superuser?: boolean;
    is_verified?: boolean;
    is_researcher: boolean;
};

export type UserUpdate = {
    password?: (string | null);
    email?: (string | null);
    is_active?: (boolean | null);
    is_superuser?: (boolean | null);
    is_verified?: (boolean | null);
    is_researcher?: (boolean | null);
};

export type ValidationError = {
    loc: Array<(string | number)>;
    msg: string;
    type: string;
};

export type GetLanguagesResponse = (Array<(string)>);

export type GetLanguagesError = unknown;

export type GetMilestonesResponse = (Array<MilestonePublic>);

export type GetMilestonesError = unknown;

export type GetMilestoneData = {
    path: {
        milestone_id: number;
    };
};

export type GetMilestoneResponse = (MilestonePublic);

export type GetMilestoneError = (HTTPValidationError);

export type GetMilestoneGroupsResponse = (Array<MilestoneGroupPublic>);

export type GetMilestoneGroupsError = unknown;

export type GetMilestoneGroupData = {
    path: {
        milestone_group_id: number;
    };
};

export type GetMilestoneGroupResponse = (MilestoneGroupPublic);

export type GetMilestoneGroupError = (HTTPValidationError);

export type GetUserQuestionsResponse = (Array<UserQuestionPublic>);

export type GetUserQuestionsError = unknown;

export type GetChildQuestionsResponse = Array<ChildQuestionPublic>;

export type GetChildQuestionsError = unknown;

export type CreateLanguageData = {
    body: Language;
};

export type CreateLanguageResponse = (Language);

export type CreateLanguageError = (HTTPValidationError);

export type DeleteLanguageData = {
    path: {
        language_id: string;
    };
};

export type DeleteLanguageResponse = (unknown);

export type DeleteLanguageError = (HTTPValidationError);

export type UpdateI18NData = {
    body: {
        [key: string]: {
            [key: string]: (string);
        };
    };
    path: {
        language_id: string;
    };
};

export type UpdateI18NResponse = (unknown);

export type UpdateI18NError = (HTTPValidationError);

export type GetMilestoneGroupsAdminResponse = (Array<MilestoneGroupAdmin>);

export type GetMilestoneGroupsAdminError = unknown;

export type CreateMilestoneGroupAdminResponse = (MilestoneGroupAdmin);

export type CreateMilestoneGroupAdminError = unknown;

export type UpdateMilestoneGroupAdminData = {
    body: MilestoneGroupAdmin;
};

export type UpdateMilestoneGroupAdminResponse = (MilestoneGroupAdmin);

export type UpdateMilestoneGroupAdminError = (HTTPValidationError);

export type DeleteMilestoneGroupAdminData = {
    path: {
        milestone_group_id: number;
    };
};

export type DeleteMilestoneGroupAdminResponse = (unknown);

export type DeleteMilestoneGroupAdminError = (HTTPValidationError);

export type UploadMilestoneGroupImageData = {
    body: Body_upload_milestone_group_image_admin_milestone_group_images__milestone_group_id__put;
    path: {
        milestone_group_id: number;
    };
};

export type UploadMilestoneGroupImageResponse = (unknown);

export type UploadMilestoneGroupImageError = (HTTPValidationError);

export type CreateMilestoneData = {
    path: {
        milestone_group_id: number;
    };
};

export type CreateMilestoneResponse = (MilestoneAdmin);

export type CreateMilestoneError = (HTTPValidationError);

export type UpdateMilestoneData = {
    body: MilestoneAdmin;
};

export type UpdateMilestoneResponse = (MilestoneAdmin);

export type UpdateMilestoneError = (HTTPValidationError);

export type DeleteMilestoneData = {
    path: {
        milestone_id: number;
    };
};

export type DeleteMilestoneResponse = (unknown);

export type DeleteMilestoneError = (HTTPValidationError);

export type UploadMilestoneImageData = {
    body: Body_upload_milestone_image_admin_milestone_images__milestone_id__post;
    path: {
        milestone_id: number;
    };
};

export type UploadMilestoneImageResponse = (MilestoneImage);

export type UploadMilestoneImageError = (HTTPValidationError);

export type GetUserQuestionsAdminResponse = (Array<UserQuestionAdmin>);

export type GetUserQuestionsAdminError = unknown;

export type UpdateUserQuestionData = {
    body: UserQuestionAdmin;
};

export type UpdateUserQuestionResponse = (UserQuestionAdmin);

export type UpdateUserQuestionError = (HTTPValidationError);

export type CreateUserQuestionResponse = (UserQuestionAdmin);

export type CreateUserQuestionError = unknown;

export type DeleteUserQuestionData = {
    path: {
        user_question_id: number;
    };
};

export type DeleteUserQuestionResponse = (unknown);

export type DeleteUserQuestionError = (HTTPValidationError);

export type UsersCurrentUserResponse = (UserRead);

export type UsersCurrentUserError = (unknown);

export type UsersPatchCurrentUserData = {
    body: UserUpdate;
};

export type UsersPatchCurrentUserResponse = (UserRead);

export type UsersPatchCurrentUserError = (ErrorModel | unknown | HTTPValidationError);

export type UsersUserData = {
    path: {
        id: string;
    };
};

export type UsersUserResponse = (UserRead);

export type UsersUserError = (unknown | HTTPValidationError);

export type UsersPatchUserData = {
    body: UserUpdate;
    path: {
        id: string;
    };
};

export type UsersPatchUserResponse = (UserRead);

export type UsersPatchUserError = (ErrorModel | unknown | HTTPValidationError);

export type UsersDeleteUserData = {
    path: {
        id: string;
    };
};

export type UsersDeleteUserResponse = (void);

export type UsersDeleteUserError = (unknown | HTTPValidationError);

export type GetChildrenResponse = (Array<ChildPublic>);

export type GetChildrenError = unknown;

export type UpdateChildData = {
    body: ChildPublic;
};

export type UpdateChildResponse = (ChildPublic);

export type UpdateChildError = (HTTPValidationError);

export type CreateChildData = {
    body: ChildCreate;
};

export type CreateChildResponse = (ChildPublic);

export type CreateChildError = (HTTPValidationError);

export type DeleteChildData = {
    path: {
        child_id: number;
    };
};

export type DeleteChildResponse = (unknown);

export type DeleteChildError = (HTTPValidationError);

export type GetChildImageData = {
    path: {
        child_id: number;
    };
};

export type GetChildImageResponse = (unknown);

export type GetChildImageError = (HTTPValidationError);

export type UploadChildImageData = {
    body: Body_upload_child_image_users_children_images__child_id__put;
    path: {
        child_id: number;
    };
};

export type UploadChildImageResponse = (unknown);

export type UploadChildImageError = (HTTPValidationError);

export type GetCurrentMilestoneAnswerSessionData = {
    path: {
        child_id: number;
    };
};

export type GetCurrentMilestoneAnswerSessionResponse = (MilestoneAnswerSessionPublic);

export type GetCurrentMilestoneAnswerSessionError = (HTTPValidationError);

export type UpdateMilestoneAnswerData = {
    body: MilestoneAnswerPublic;
    path: {
        milestone_answer_session_id: number;
    };
};

export type UpdateMilestoneAnswerResponse = (MilestoneAnswerPublic);

export type UpdateMilestoneAnswerError = (HTTPValidationError);

export type GetCurrentUserAnswersResponse = (Array<UserAnswerPublic>);

export type GetCurrentUserAnswersError = unknown;

export type UpdateCurrentUserAnswersData = {
    body: Array<UserAnswerPublic>;
};

export type UpdateCurrentUserAnswersResponse = (Array<UserAnswerPublic>);

export type UpdateCurrentUserAnswersError = (HTTPValidationError);

export type GetCurrentChildrenAnswersResponse = Array<ChildAnswerPublic>;

export type GetCurrentChildrenAnswersError = unknown;

export type UpdateCurrentChildrenAnswersData = {
	body: Array<ChildAnswerPublic>;
};

export type UpdateCurrentChildrenAnswersResponse = Array<ChildAnswerPublic>;

export type UpdateCurrentChildrenAnswersError = HTTPValidationError;

export type AuthCookieLoginData = {
    body: Body_auth_cookie_login_auth_login_post;
};

export type AuthCookieLoginResponse = (unknown | void);

export type AuthCookieLoginError = (ErrorModel | HTTPValidationError);

export type AuthCookieLogoutResponse = (unknown | void);

export type AuthCookieLogoutError = (unknown);

export type RegisterRegisterData = {
    body: UserCreate;
};

export type RegisterRegisterResponse = (UserRead);

export type RegisterRegisterError = (ErrorModel | HTTPValidationError);

export type ResetForgotPasswordData = {
    body: Body_reset_forgot_password_auth_forgot_password_post;
};

export type ResetForgotPasswordResponse = (unknown);

export type ResetForgotPasswordError = (HTTPValidationError);

export type ResetResetPasswordData = {
    body: Body_reset_reset_password_auth_reset_password_post;
};

export type ResetResetPasswordResponse = (unknown);

export type ResetResetPasswordError = (ErrorModel | HTTPValidationError);

export type VerifyRequestTokenData = {
    body: Body_verify_request_token_auth_request_verify_token_post;
};

export type VerifyRequestTokenResponse = (unknown);

export type VerifyRequestTokenError = (HTTPValidationError);

export type VerifyVerifyData = {
    body: Body_verify_verify_auth_verify_post;
};

export type VerifyVerifyResponse = (UserRead);

export type VerifyVerifyError = (ErrorModel | HTTPValidationError);

export type AuthResponse = (unknown);

export type AuthError = unknown;