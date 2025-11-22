'use client'

import { useState } from 'react'
import { ChevronLeft, ChevronRight, Check, Info, AlertCircle } from 'lucide-react'

interface WizardStep {
  id: string
  title: string
  description: string
  component: React.ReactNode
  isValid: boolean
}

interface AlertWizardProps {
  children: (step: number, setStep: (step: number) => void, data: any, updateData: (data: any) => void) => WizardStep[]
  onSubmit: (data: any) => Promise<void>
  onCancel: () => void
}

export default function AlertWizard({ children, onSubmit, onCancel }: AlertWizardProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState<any>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const steps = children(currentStep, setCurrentStep, formData, setFormData)

  const updateFormData = (updates: any) => {
    setFormData((prev: any) => ({ ...prev, ...updates }))
  }

  const goToStep = (step: number) => {
    if (step >= 0 && step < steps.length) {
      setCurrentStep(step)
    }
  }

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      goToStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      goToStep(currentStep - 1)
    }
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    try {
      await onSubmit(formData)
    } finally {
      setIsSubmitting(false)
    }
  }

  const currentStepData = steps[currentStep]
  const canProceed = currentStepData?.isValid ?? false
  const isLastStep = currentStep === steps.length - 1

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Progress Bar */}
      <div className="bg-white/10 backdrop-blur-lg border-b border-white/20">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center flex-1">
                <div
                  className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all ${
                    index < currentStep
                      ? 'bg-green-500 border-green-500 text-white'
                      : index === currentStep
                      ? 'bg-blue-600 border-blue-600 text-white'
                      : 'bg-transparent border-gray-600 text-gray-400'
                  }`}
                >
                  {index < currentStep ? (
                    <Check className="w-5 h-5" />
                  ) : (
                    <span className="font-semibold">{index + 1}</span>
                  )}
                </div>
                <div className="ml-3 flex-1">
                  <div
                    className={`text-sm font-medium ${
                      index <= currentStep ? 'text-white' : 'text-gray-400'
                    }`}
                  >
                    {step.title}
                  </div>
                  <div className="text-xs text-gray-400 hidden md:block">{step.description}</div>
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={`hidden md:block h-1 flex-1 mx-4 rounded ${
                      index < currentStep ? 'bg-green-500' : 'bg-gray-700'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Step Content */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-white/10 backdrop-blur-xl rounded-xl p-8 border border-white/20 shadow-2xl">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-white mb-2">{currentStepData?.title}</h2>
            <p className="text-gray-300">{currentStepData?.description}</p>
          </div>

          <div className="min-h-[400px]">
            {currentStepData?.component}
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-between mt-8 pt-6 border-t border-white/20">
            <button
              onClick={currentStep === 0 ? onCancel : prevStep}
              className="flex items-center px-6 py-3 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
            >
              <ChevronLeft className="w-5 h-5 mr-2" />
              {currentStep === 0 ? 'Cancel' : 'Back'}
            </button>

            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <span>Step {currentStep + 1} of {steps.length}</span>
            </div>

            {isLastStep ? (
              <button
                onClick={handleSubmit}
                disabled={!canProceed || isSubmitting}
                className="flex items-center px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Creating...
                  </>
                ) : (
                  <>
                    <Check className="w-5 h-5 mr-2" />
                    Create Alert
                  </>
                )}
              </button>
            ) : (
              <button
                onClick={nextStep}
                disabled={!canProceed}
                className="flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
                <ChevronRight className="w-5 h-5 ml-2" />
              </button>
            )}
          </div>

          {/* Validation Message */}
          {!canProceed && (
            <div className="mt-4 flex items-center text-yellow-400 text-sm">
              <AlertCircle className="w-4 h-4 mr-2" />
              Please complete all required fields to continue
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

