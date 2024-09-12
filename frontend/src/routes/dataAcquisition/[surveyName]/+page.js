import { content, createDummyData } from '$lib/stores/contentStore';
import { error } from '@sveltejs/kit';

/** @type {import('./$types').PageLoad}     */
export async function load({ params }) {
	createDummyData();
	const data = await content.fetch(params.surveyName);
	if (!data) {
		error(404, `Survey ${params.surveyName} not found`);
	}
	return {
		surveyName: params.surveyName,
		data: data
	};
}
export const prerender = false;