import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Pricing: React.FC = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);

  const handleSubscribe = async (planId: string) => {
    if (!user) {
      // Redirect to login
      window.location.href = '/login';
      return;
    }

    setLoading(true);
    try {
      // In a real implementation, you would integrate with Stripe here
      console.log('Subscribing to plan:', planId);
      // For now, just show a message
      alert('Payment integration coming soon!');
    } catch (error) {
      console.error('Subscription failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const plans = [
    {
      id: 'basic',
      name: 'Basic Plan',
      price: 29.99,
      currency: 'usd',
      interval: 'month',
      features: [
        'Access to UX Workflow Agent',
        'Basic UX knowledge base',
        '5 conversations per month',
        'Email support'
      ],
      popular: false
    },
    {
      id: 'premium',
      name: 'Premium Plan',
      price: 99.99,
      currency: 'usd',
      interval: 'month',
      features: [
        'Access to all UX agents',
        'Full UX knowledge base',
        'Unlimited conversations',
        'Priority support',
        'Advanced analytics',
        'Custom integrations'
      ],
      popular: true
    }
  ];

  return (
    <div className="bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
            Simple, transparent pricing
          </h2>
          <p className="mt-4 text-lg text-gray-600">
            Choose the plan that's right for your team
          </p>
        </div>

        <div className="mt-12 space-y-4 sm:mt-16 sm:space-y-0 sm:grid sm:grid-cols-2 sm:gap-6 lg:max-w-4xl lg:mx-auto xl:max-w-none xl:mx-0 xl:grid-cols-2">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`relative p-8 bg-white border rounded-2xl shadow-sm flex flex-col ${
                plan.popular ? 'border-indigo-500 ring-1 ring-indigo-500' : 'border-gray-200'
              }`}
            >
              {plan.popular && (
                <div className="absolute top-0 py-1.5 px-4 bg-indigo-500 rounded-full text-xs font-semibold uppercase tracking-wide text-white transform -translate-y-1/2 left-1/2 -translate-x-1/2">
                  Most popular
                </div>
              )}
              
              <div className="flex-1">
                <h3 className="text-xl font-semibold text-gray-900">{plan.name}</h3>
                <p className="mt-4 flex items-baseline text-gray-900">
                  <span className="text-5xl font-extrabold tracking-tight">
                    ${plan.price}
                  </span>
                  <span className="ml-1 text-xl font-semibold">/{plan.interval}</span>
                </p>
                <p className="mt-6 text-gray-500">
                  Perfect for {plan.id === 'basic' ? 'small teams getting started' : 'enterprise teams'}
                </p>

                <ul className="mt-6 space-y-6">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex">
                      <svg
                        className="flex-shrink-0 w-6 h-6 text-indigo-500"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                      <span className="ml-3 text-gray-500">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <button
                onClick={() => handleSubscribe(plan.id)}
                disabled={loading}
                className={`mt-8 block w-full py-3 px-6 border border-transparent rounded-md text-center font-medium ${
                  plan.popular
                    ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                    : 'bg-indigo-50 text-indigo-700 hover:bg-indigo-100'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {loading ? 'Processing...' : user?.is_premium ? 'Current Plan' : 'Get Started'}
              </button>
            </div>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="mt-16">
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Frequently Asked Questions
          </h3>
          <div className="max-w-3xl mx-auto space-y-8">
            <div>
              <h4 className="text-lg font-medium text-gray-900">
                What's included in the UX knowledge base?
              </h4>
              <p className="mt-2 text-gray-600">
                Our knowledge base includes comprehensive UX methodologies, best practices, 
                case studies, and industry insights specifically curated for B2B enterprise applications.
              </p>
            </div>
            <div>
              <h4 className="text-lg font-medium text-gray-900">
                Can I change plans anytime?
              </h4>
              <p className="mt-2 text-gray-600">
                Yes, you can upgrade or downgrade your plan at any time. Changes take effect 
                immediately, and we'll prorate any billing differences.
              </p>
            </div>
            <div>
              <h4 className="text-lg font-medium text-gray-900">
                Is there a free trial?
              </h4>
              <p className="mt-2 text-gray-600">
                We offer a 14-day free trial for all new users. No credit card required to start.
              </p>
            </div>
            <div>
              <h4 className="text-lg font-medium text-gray-900">
                What kind of support do you provide?
              </h4>
              <p className="mt-2 text-gray-600">
                Basic plan includes email support, while Premium plan includes priority support 
                with faster response times and dedicated account management.
              </p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-16 bg-indigo-700 rounded-2xl">
          <div className="px-6 py-12 sm:px-12 lg:px-16">
            <div className="text-center">
              <h3 className="text-2xl font-bold text-white">
                Ready to transform your UX workflow?
              </h3>
              <p className="mt-4 text-lg text-indigo-200">
                Join enterprise teams already using our AI agents to improve their UX processes.
              </p>
              <div className="mt-8">
                {user ? (
                  <Link
                    to="/dashboard"
                    className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-indigo-600 bg-white hover:bg-indigo-50"
                  >
                    Go to Dashboard
                  </Link>
                ) : (
                  <Link
                    to="/register"
                    className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-indigo-600 bg-white hover:bg-indigo-50"
                  >
                    Start Free Trial
                  </Link>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Pricing;
