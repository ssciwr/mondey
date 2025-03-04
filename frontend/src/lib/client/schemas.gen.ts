// This file is auto-generated by @hey-api/openapi-ts

export const Body_auth_cookie_login_auth_login_postSchema = {
    properties: {
        grant_type: {
            anyOf: [
                {
                    type: 'string',
                    pattern: '^password$'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Grant Type'
        },
        username: {
            type: 'string',
            title: 'Username'
        },
        password: {
            type: 'string',
            title: 'Password'
        },
        scope: {
            type: 'string',
            title: 'Scope',
            default: ''
        },
        client_id: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Client Id'
        },
        client_secret: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Client Secret'
        }
    },
    type: 'object',
    required: ['username', 'password'],
    title: 'Body_auth_cookie_login_auth_login_post'
} as const;

export const Body_reset_forgot_password_auth_forgot_password_postSchema = {
    properties: {
        email: {
            type: 'string',
            format: 'email',
            title: 'Email'
        }
    },
    type: 'object',
    required: ['email'],
    title: 'Body_reset_forgot_password_auth_forgot_password_post'
} as const;

export const Body_reset_reset_password_auth_reset_password_postSchema = {
    properties: {
        token: {
            type: 'string',
            title: 'Token'
        },
        password: {
            type: 'string',
            title: 'Password'
        }
    },
    type: 'object',
    required: ['token', 'password'],
    title: 'Body_reset_reset_password_auth_reset_password_post'
} as const;

export const Body_submit_milestone_image_submitted_milestone_images__milestone_id__postSchema = {
    properties: {
        file: {
            type: 'string',
            format: 'binary',
            title: 'File'
        }
    },
    type: 'object',
    required: ['file'],
    title: 'Body_submit_milestone_image_submitted_milestone_images__milestone_id__post'
} as const;

export const Body_upload_child_image_users_children_images__child_id__putSchema = {
    properties: {
        file: {
            type: 'string',
            format: 'binary',
            title: 'File'
        }
    },
    type: 'object',
    required: ['file'],
    title: 'Body_upload_child_image_users_children_images__child_id__put'
} as const;

export const Body_upload_milestone_group_image_admin_milestone_group_images__milestone_group_id__putSchema = {
    properties: {
        file: {
            type: 'string',
            format: 'binary',
            title: 'File'
        }
    },
    type: 'object',
    required: ['file'],
    title: 'Body_upload_milestone_group_image_admin_milestone_group_images__milestone_group_id__put'
} as const;

export const Body_upload_milestone_image_admin_milestone_images__milestone_id__postSchema = {
    properties: {
        file: {
            type: 'string',
            format: 'binary',
            title: 'File'
        }
    },
    type: 'object',
    required: ['file'],
    title: 'Body_upload_milestone_image_admin_milestone_images__milestone_id__post'
} as const;

export const Body_verify_request_token_auth_request_verify_token_postSchema = {
    properties: {
        email: {
            type: 'string',
            format: 'email',
            title: 'Email'
        }
    },
    type: 'object',
    required: ['email'],
    title: 'Body_verify_request_token_auth_request_verify_token_post'
} as const;

export const Body_verify_verify_auth_verify_postSchema = {
    properties: {
        token: {
            type: 'string',
            title: 'Token'
        }
    },
    type: 'object',
    required: ['token'],
    title: 'Body_verify_verify_auth_verify_post'
} as const;

export const ChildAnswerPublicSchema = {
    properties: {
        answer: {
            type: 'string',
            title: 'Answer'
        },
        additional_answer: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Additional Answer'
        },
        question_id: {
            type: 'integer',
            title: 'Question Id'
        }
    },
    type: 'object',
    required: ['answer', 'additional_answer', 'question_id'],
    title: 'ChildAnswerPublic'
} as const;

export const ChildCreateSchema = {
    properties: {
        name: {
            type: 'string',
            title: 'Name',
            default: ''
        },
        birth_year: {
            type: 'integer',
            title: 'Birth Year'
        },
        birth_month: {
            type: 'integer',
            title: 'Birth Month'
        },
        color: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Color'
        }
    },
    type: 'object',
    required: ['birth_year', 'birth_month'],
    title: 'ChildCreate'
} as const;

export const ChildPublicSchema = {
    properties: {
        name: {
            type: 'string',
            title: 'Name',
            default: ''
        },
        birth_year: {
            type: 'integer',
            title: 'Birth Year'
        },
        birth_month: {
            type: 'integer',
            title: 'Birth Month'
        },
        color: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Color'
        },
        id: {
            type: 'integer',
            title: 'Id'
        },
        has_image: {
            type: 'boolean',
            title: 'Has Image'
        }
    },
    type: 'object',
    required: ['birth_year', 'birth_month', 'id', 'has_image'],
    title: 'ChildPublic'
} as const;

export const ChildQuestionAdminSchema = {
    properties: {
        order: {
            type: 'integer',
            title: 'Order',
            default: 0
        },
        component: {
            type: 'string',
            title: 'Component',
            default: 'select'
        },
        type: {
            type: 'string',
            title: 'Type',
            default: 'text'
        },
        options: {
            type: 'string',
            title: 'Options',
            default: ''
        },
        additional_option: {
            type: 'string',
            title: 'Additional Option',
            default: ''
        },
        id: {
            type: 'integer',
            title: 'Id'
        },
        text: {
            additionalProperties: {
                '$ref': '#/components/schemas/ChildQuestionText'
            },
            type: 'object',
            title: 'Text',
            default: {}
        }
    },
    type: 'object',
    required: ['id'],
    title: 'ChildQuestionAdmin'
} as const;

export const ChildQuestionPublicSchema = {
    properties: {
        id: {
            type: 'integer',
            title: 'Id'
        },
        component: {
            type: 'string',
            title: 'Component',
            default: 'select'
        },
        type: {
            type: 'string',
            title: 'Type',
            default: 'text'
        },
        text: {
            additionalProperties: {
                '$ref': '#/components/schemas/QuestionTextPublic'
            },
            type: 'object',
            title: 'Text',
            default: {}
        },
        additional_option: {
            type: 'string',
            title: 'Additional Option',
            default: ''
        }
    },
    type: 'object',
    required: ['id'],
    title: 'ChildQuestionPublic'
} as const;

export const ChildQuestionTextSchema = {
    properties: {
        question: {
            type: 'string',
            title: 'Question',
            default: ''
        },
        options_json: {
            type: 'string',
            title: 'Options Json',
            default: ''
        },
        options: {
            type: 'string',
            title: 'Options',
            default: ''
        },
        child_question_id: {
            anyOf: [
                {
                    type: 'integer'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Child Question Id'
        },
        lang_id: {
            anyOf: [
                {
                    type: 'string',
                    maxLength: 2
                },
                {
                    type: 'null'
                }
            ],
            title: 'Lang Id'
        }
    },
    type: 'object',
    title: 'ChildQuestionText'
} as const;

export const ErrorModelSchema = {
    properties: {
        detail: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    additionalProperties: {
                        type: 'string'
                    },
                    type: 'object'
                }
            ],
            title: 'Detail'
        }
    },
    type: 'object',
    required: ['detail'],
    title: 'ErrorModel'
} as const;

export const HTTPValidationErrorSchema = {
    properties: {
        detail: {
            items: {
                '$ref': '#/components/schemas/ValidationError'
            },
            type: 'array',
            title: 'Detail'
        }
    },
    type: 'object',
    title: 'HTTPValidationError'
} as const;

export const ItemOrderSchema = {
    properties: {
        id: {
            type: 'integer',
            title: 'Id'
        },
        order: {
            type: 'integer',
            title: 'Order'
        }
    },
    type: 'object',
    required: ['id', 'order'],
    title: 'ItemOrder'
} as const;

export const LanguageSchema = {
    properties: {
        id: {
            type: 'string',
            maxLength: 2,
            title: 'Id'
        }
    },
    type: 'object',
    required: ['id'],
    title: 'Language'
} as const;

export const MilestoneAdminSchema = {
    properties: {
        id: {
            type: 'integer',
            title: 'Id'
        },
        group_id: {
            type: 'integer',
            title: 'Group Id'
        },
        order: {
            type: 'integer',
            title: 'Order'
        },
        expected_age_months: {
            type: 'integer',
            title: 'Expected Age Months'
        },
        text: {
            additionalProperties: {
                '$ref': '#/components/schemas/MilestoneText'
            },
            type: 'object',
            title: 'Text'
        },
        images: {
            items: {
                '$ref': '#/components/schemas/MilestoneImage'
            },
            type: 'array',
            title: 'Images'
        }
    },
    type: 'object',
    required: ['id', 'group_id', 'order', 'expected_age_months', 'text', 'images'],
    title: 'MilestoneAdmin'
} as const;

export const MilestoneAgeScoreSchema = {
    properties: {
        milestone_id: {
            anyOf: [
                {
                    type: 'integer'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Milestone Id'
        },
        age: {
            type: 'integer',
            title: 'Age'
        },
        count: {
            type: 'integer',
            title: 'Count'
        },
        avg_score: {
            type: 'number',
            title: 'Avg Score'
        },
        stddev_score: {
            type: 'number',
            title: 'Stddev Score'
        },
        expected_score: {
            type: 'number',
            title: 'Expected Score'
        }
    },
    type: 'object',
    required: ['age', 'count', 'avg_score', 'stddev_score', 'expected_score'],
    title: 'MilestoneAgeScore'
} as const;

export const MilestoneAgeScoreCollectionPublicSchema = {
    properties: {
        milestone_id: {
            type: 'integer',
            title: 'Milestone Id'
        },
        expected_age: {
            type: 'integer',
            title: 'Expected Age'
        },
        scores: {
            items: {
                '$ref': '#/components/schemas/MilestoneAgeScore'
            },
            type: 'array',
            title: 'Scores'
        }
    },
    type: 'object',
    required: ['milestone_id', 'expected_age', 'scores'],
    title: 'MilestoneAgeScoreCollectionPublic'
} as const;

export const MilestoneAnswerPublicSchema = {
    properties: {
        milestone_id: {
            type: 'integer',
            title: 'Milestone Id'
        },
        answer: {
            type: 'integer',
            title: 'Answer'
        }
    },
    type: 'object',
    required: ['milestone_id', 'answer'],
    title: 'MilestoneAnswerPublic'
} as const;

export const MilestoneAnswerSessionPublicSchema = {
    properties: {
        id: {
            type: 'integer',
            title: 'Id'
        },
        child_id: {
            type: 'integer',
            title: 'Child Id'
        },
        created_at: {
            type: 'string',
            format: 'date-time',
            title: 'Created At'
        },
        answers: {
            additionalProperties: {
                '$ref': '#/components/schemas/MilestoneAnswerPublic'
            },
            type: 'object',
            title: 'Answers'
        }
    },
    type: 'object',
    required: ['id', 'child_id', 'created_at', 'answers'],
    title: 'MilestoneAnswerSessionPublic'
} as const;

export const MilestoneGroupAdminSchema = {
    properties: {
        id: {
            type: 'integer',
            title: 'Id'
        },
        order: {
            type: 'integer',
            title: 'Order'
        },
        text: {
            additionalProperties: {
                '$ref': '#/components/schemas/MilestoneGroupText'
            },
            type: 'object',
            title: 'Text'
        },
        milestones: {
            items: {
                '$ref': '#/components/schemas/MilestoneAdmin'
            },
            type: 'array',
            title: 'Milestones'
        }
    },
    type: 'object',
    required: ['id', 'order', 'text', 'milestones'],
    title: 'MilestoneGroupAdmin'
} as const;

export const MilestoneGroupPublicSchema = {
    properties: {
        id: {
            type: 'integer',
            title: 'Id'
        },
        text: {
            additionalProperties: {
                '$ref': '#/components/schemas/MilestoneGroupTextPublic'
            },
            type: 'object',
            title: 'Text'
        },
        milestones: {
            items: {
                '$ref': '#/components/schemas/MilestonePublic'
            },
            type: 'array',
            title: 'Milestones'
        }
    },
    type: 'object',
    required: ['id', 'text', 'milestones'],
    title: 'MilestoneGroupPublic'
} as const;

export const MilestoneGroupTextSchema = {
    properties: {
        title: {
            type: 'string',
            title: 'Title',
            default: ''
        },
        desc: {
            type: 'string',
            title: 'Desc',
            default: ''
        },
        group_id: {
            anyOf: [
                {
                    type: 'integer'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Group Id'
        },
        lang_id: {
            anyOf: [
                {
                    type: 'string',
                    maxLength: 2
                },
                {
                    type: 'null'
                }
            ],
            title: 'Lang Id'
        }
    },
    type: 'object',
    title: 'MilestoneGroupText'
} as const;

export const MilestoneGroupTextPublicSchema = {
    properties: {
        title: {
            type: 'string',
            title: 'Title',
            default: ''
        },
        desc: {
            type: 'string',
            title: 'Desc',
            default: ''
        }
    },
    type: 'object',
    title: 'MilestoneGroupTextPublic'
} as const;

export const MilestoneImageSchema = {
    properties: {
        id: {
            anyOf: [
                {
                    type: 'integer'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Id'
        },
        milestone_id: {
            anyOf: [
                {
                    type: 'integer'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Milestone Id'
        }
    },
    type: 'object',
    title: 'MilestoneImage'
} as const;

export const MilestoneImagePublicSchema = {
    properties: {
        id: {
            type: 'integer',
            title: 'Id'
        }
    },
    type: 'object',
    required: ['id'],
    title: 'MilestoneImagePublic'
} as const;

export const MilestonePublicSchema = {
    properties: {
        id: {
            type: 'integer',
            title: 'Id'
        },
        expected_age_months: {
            type: 'integer',
            title: 'Expected Age Months'
        },
        text: {
            additionalProperties: {
                '$ref': '#/components/schemas/MilestoneTextPublic'
            },
            type: 'object',
            title: 'Text'
        },
        images: {
            items: {
                '$ref': '#/components/schemas/MilestoneImagePublic'
            },
            type: 'array',
            title: 'Images'
        }
    },
    type: 'object',
    required: ['id', 'expected_age_months', 'text', 'images'],
    title: 'MilestonePublic'
} as const;

export const MilestoneTextSchema = {
    properties: {
        title: {
            type: 'string',
            title: 'Title',
            default: ''
        },
        desc: {
            type: 'string',
            title: 'Desc',
            default: ''
        },
        obs: {
            type: 'string',
            title: 'Obs',
            default: ''
        },
        help: {
            type: 'string',
            title: 'Help',
            default: ''
        },
        milestone_id: {
            anyOf: [
                {
                    type: 'integer'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Milestone Id'
        },
        lang_id: {
            anyOf: [
                {
                    type: 'string',
                    maxLength: 2
                },
                {
                    type: 'null'
                }
            ],
            title: 'Lang Id'
        }
    },
    type: 'object',
    title: 'MilestoneText'
} as const;

export const MilestoneTextPublicSchema = {
    properties: {
        title: {
            type: 'string',
            title: 'Title',
            default: ''
        },
        desc: {
            type: 'string',
            title: 'Desc',
            default: ''
        },
        obs: {
            type: 'string',
            title: 'Obs',
            default: ''
        },
        help: {
            type: 'string',
            title: 'Help',
            default: ''
        }
    },
    type: 'object',
    title: 'MilestoneTextPublic'
} as const;

export const QuestionTextPublicSchema = {
    properties: {
        question: {
            type: 'string',
            title: 'Question',
            default: ''
        },
        options_json: {
            type: 'string',
            title: 'Options Json',
            default: ''
        },
        options: {
            type: 'string',
            title: 'Options',
            default: ''
        }
    },
    type: 'object',
    title: 'QuestionTextPublic'
} as const;

export const ResearchGroupSchema = {
    properties: {
        id: {
            type: 'integer',
            title: 'Id'
        }
    },
    type: 'object',
    required: ['id'],
    title: 'ResearchGroup'
} as const;

export const SubmittedMilestoneImagePublicSchema = {
    properties: {
        id: {
            type: 'integer',
            title: 'Id'
        },
        milestone_id: {
            type: 'integer',
            title: 'Milestone Id'
        },
        user_id: {
            type: 'integer',
            title: 'User Id'
        }
    },
    type: 'object',
    required: ['id', 'milestone_id', 'user_id'],
    title: 'SubmittedMilestoneImagePublic'
} as const;

export const UserAnswerPublicSchema = {
    properties: {
        answer: {
            type: 'string',
            title: 'Answer'
        },
        additional_answer: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Additional Answer'
        },
        question_id: {
            type: 'integer',
            title: 'Question Id'
        }
    },
    type: 'object',
    required: ['answer', 'additional_answer', 'question_id'],
    title: 'UserAnswerPublic'
} as const;

export const UserCreateSchema = {
    properties: {
        email: {
            type: 'string',
            format: 'email',
            title: 'Email'
        },
        password: {
            type: 'string',
            title: 'Password'
        },
        is_active: {
            anyOf: [
                {
                    type: 'boolean'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Is Active',
            default: true
        },
        is_superuser: {
            anyOf: [
                {
                    type: 'boolean'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Is Superuser',
            default: false
        },
        is_verified: {
            anyOf: [
                {
                    type: 'boolean'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Is Verified',
            default: false
        },
        is_researcher: {
            anyOf: [
                {
                    type: 'boolean'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Is Researcher',
            default: false
        },
        full_data_access: {
            anyOf: [
                {
                    type: 'boolean'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Full Data Access',
            default: false
        },
        research_group_id: {
            anyOf: [
                {
                    type: 'integer'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Research Group Id',
            default: 0
        }
    },
    type: 'object',
    required: ['email', 'password'],
    title: 'UserCreate'
} as const;

export const UserQuestionAdminSchema = {
    properties: {
        order: {
            type: 'integer',
            title: 'Order',
            default: 0
        },
        component: {
            type: 'string',
            title: 'Component',
            default: 'select'
        },
        type: {
            type: 'string',
            title: 'Type',
            default: 'text'
        },
        options: {
            type: 'string',
            title: 'Options',
            default: ''
        },
        additional_option: {
            type: 'string',
            title: 'Additional Option',
            default: ''
        },
        id: {
            type: 'integer',
            title: 'Id'
        },
        text: {
            additionalProperties: {
                '$ref': '#/components/schemas/UserQuestionText'
            },
            type: 'object',
            title: 'Text',
            default: {}
        }
    },
    type: 'object',
    required: ['id'],
    title: 'UserQuestionAdmin'
} as const;

export const UserQuestionPublicSchema = {
    properties: {
        id: {
            type: 'integer',
            title: 'Id'
        },
        component: {
            type: 'string',
            title: 'Component',
            default: 'select'
        },
        type: {
            type: 'string',
            title: 'Type',
            default: 'text'
        },
        text: {
            additionalProperties: {
                '$ref': '#/components/schemas/QuestionTextPublic'
            },
            type: 'object',
            title: 'Text',
            default: {}
        },
        additional_option: {
            type: 'string',
            title: 'Additional Option',
            default: ''
        }
    },
    type: 'object',
    required: ['id'],
    title: 'UserQuestionPublic'
} as const;

export const UserQuestionTextSchema = {
    properties: {
        question: {
            type: 'string',
            title: 'Question',
            default: ''
        },
        options_json: {
            type: 'string',
            title: 'Options Json',
            default: ''
        },
        options: {
            type: 'string',
            title: 'Options',
            default: ''
        },
        user_question_id: {
            anyOf: [
                {
                    type: 'integer'
                },
                {
                    type: 'null'
                }
            ],
            title: 'User Question Id'
        },
        lang_id: {
            anyOf: [
                {
                    type: 'string',
                    maxLength: 2
                },
                {
                    type: 'null'
                }
            ],
            title: 'Lang Id'
        }
    },
    type: 'object',
    title: 'UserQuestionText'
} as const;

export const UserReadSchema = {
    properties: {
        id: {
            type: 'integer',
            title: 'Id'
        },
        email: {
            type: 'string',
            format: 'email',
            title: 'Email'
        },
        is_active: {
            type: 'boolean',
            title: 'Is Active',
            default: true
        },
        is_superuser: {
            type: 'boolean',
            title: 'Is Superuser',
            default: false
        },
        is_verified: {
            type: 'boolean',
            title: 'Is Verified',
            default: false
        },
        is_researcher: {
            type: 'boolean',
            title: 'Is Researcher'
        },
        full_data_access: {
            type: 'boolean',
            title: 'Full Data Access'
        },
        research_group_id: {
            type: 'integer',
            title: 'Research Group Id'
        }
    },
    type: 'object',
    required: ['id', 'email', 'is_researcher', 'full_data_access', 'research_group_id'],
    title: 'UserRead'
} as const;

export const UserUpdateSchema = {
    properties: {
        password: {
            anyOf: [
                {
                    type: 'string'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Password'
        },
        email: {
            anyOf: [
                {
                    type: 'string',
                    format: 'email'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Email'
        },
        is_active: {
            anyOf: [
                {
                    type: 'boolean'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Is Active'
        },
        is_superuser: {
            anyOf: [
                {
                    type: 'boolean'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Is Superuser'
        },
        is_verified: {
            anyOf: [
                {
                    type: 'boolean'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Is Verified'
        },
        is_researcher: {
            anyOf: [
                {
                    type: 'boolean'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Is Researcher'
        },
        full_data_access: {
            anyOf: [
                {
                    type: 'boolean'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Full Data Access'
        },
        research_group_id: {
            anyOf: [
                {
                    type: 'integer'
                },
                {
                    type: 'null'
                }
            ],
            title: 'Research Group Id'
        }
    },
    type: 'object',
    title: 'UserUpdate'
} as const;

export const ValidationErrorSchema = {
    properties: {
        loc: {
            items: {
                anyOf: [
                    {
                        type: 'string'
                    },
                    {
                        type: 'integer'
                    }
                ]
            },
            type: 'array',
            title: 'Location'
        },
        msg: {
            type: 'string',
            title: 'Message'
        },
        type: {
            type: 'string',
            title: 'Error Type'
        }
    },
    type: 'object',
    required: ['loc', 'msg', 'type'],
    title: 'ValidationError'
} as const;