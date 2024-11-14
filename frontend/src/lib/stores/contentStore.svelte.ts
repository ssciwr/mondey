interface Content {
	[key: string]: any;
}

function createContent() {
	const content = {} as Content;

	return {
		set milestoneGroup(value: number) {
			content.milestoneGroup = value;
		},
		set milestone(value: number) {
			content.milestone = value;
		},
		set milestoneIndex(value: number) {
			content.milestoneIndex = value;
		},
		get milestoneIndex() {
			return content.milestoneIndex;
		},
		get milestone() {
			return content.milestone;
		},
		get milestoneGroup() {
			return content.milestoneGroup;
		},
		set milestoneGroupData(value: any) {
			content.milestoneGroupData = value;
		},
		set milestoneData(value: any) {
			content.milestoneData = value;
		},
		get milestoneGroupData() {
			return content.milestoneGroupData;
		},
		get milestoneData() {
			return content.milestoneData;
		},
	};
}

export const contentStore = createContent();
